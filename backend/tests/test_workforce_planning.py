import importlib.util
import unittest


class TestWorkforcePlanning(unittest.TestCase):
    def test_fully_loaded_multiplier_and_attrition_backfill(self):
        base_salary = 200000.0
        fully_loaded = round(base_salary * 1.28, 2)
        self.assertEqual(fully_loaded, 256000.0)

        current_hc = 50
        target_hc = 60
        attrition_rate = 0.08
        net_new = target_hc - current_hc
        backfills = round(current_hc * attrition_rate)
        self.assertEqual(net_new, 10)
        self.assertEqual(backfills, 4)
        self.assertEqual(net_new + backfills, 14)

    @unittest.skipUnless(importlib.util.find_spec("pydantic_settings"), "Requires pydantic_settings")
    def test_workforce_planning_service_simulation_and_recruiter_sync(self):
        from backend.app.schemas.workforce_planning import (
            RequisitionForecastCreate,
            ScenarioForecastRequest,
            WorkforcePlanCreate,
        )
        from backend.app.services.workforce_planning_service import WorkforcePlanningService

        svc = WorkforcePlanningService()
        plan = svc.create_plan(
            WorkforcePlanCreate(
                fiscal_year=2027,
                department="Data Platform",
                current_headcount=25,
                target_headcount=35,
                approved_budget_usd=3000000.0,
                projected_attrition_rate=0.08,
            )
        )
        self.assertEqual(plan.department, "Data Platform")

        sim_baseline = svc.simulate_plan(
            plan.id, ScenarioForecastRequest(scenario="BASELINE", avg_base_salary=180000.0)
        )
        self.assertEqual(sim_baseline.net_new_hires, 10)
        self.assertEqual(sim_baseline.attrition_backfills, 2)
        self.assertEqual(sim_baseline.total_hiring_need, 12)

        sim_hyper = svc.simulate_plan(
            plan.id, ScenarioForecastRequest(scenario="HYPERGROWTH", avg_base_salary=180000.0)
        )
        self.assertGreater(sim_hyper.net_new_hires, sim_baseline.net_new_hires)

        req = svc.add_requisition(
            plan.id,
            RequisitionForecastCreate(
                role_title="Senior Data Engineer",
                job_level="L5",
                target_quarter="Q2",
                estimated_base_salary=185000.0,
            ),
        )
        self.assertEqual(req.fully_loaded_cost, 236800.0)

        sync_res = svc.sync_requisition_to_recruiter(req.id)
        self.assertEqual(sync_res.recruiter_sync_status, "SYNCED_TO_RECRUITER")
        self.assertTrue(sync_res.signed_payload["hmac_sha256"].startswith("sha256="))


if __name__ == "__main__":
    unittest.main()
