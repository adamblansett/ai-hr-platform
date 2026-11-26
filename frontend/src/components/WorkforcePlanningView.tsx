import React, { useState, useEffect } from 'react';
import { TrendingUp, Users, DollarSign, Send, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { ScenarioForecastResult, WorkforcePlan, WorkforcePlanningSummary } from '../types';

export const WorkforcePlanningView: React.FC = () => {
  const [plans, setPlans] = useState<WorkforcePlan[]>([]);
  const [summary, setSummary] = useState<WorkforcePlanningSummary | null>(null);
  const [simulation, setSimulation] = useState<ScenarioForecastResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  const [department, setDepartment] = useState('Product & Design');
  const [currentHeadcount, setCurrentHeadcount] = useState(14);
  const [targetHeadcount, setTargetHeadcount] = useState(20);
  const [budgetUsd, setBudgetUsd] = useState(1400000);

  const loadData = async () => {
    try {
      setLoading(true);
      const [planData, sumData] = await Promise.all([api.getWorkforcePlans(), api.getWorkforcePlanningSummary()]);
      setPlans(planData);
      setSummary(sumData);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load workforce planning data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSimulate = async (planId: string, scenario: 'CONSERVATIVE' | 'BASELINE' | 'HYPERGROWTH') => {
    try {
      const res = await api.simulateWorkforcePlan(planId, scenario, 175000);
      setSimulation(res);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleSyncRecruiter = async (reqId: string) => {
    try {
      const res = await api.syncRequisitionToRecruiter(reqId);
      setSyncMessage(`Synced ${reqId} to ai-recruiter (${res.webhook_event})`);
      await loadData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleCreatePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      await api.createWorkforcePlan({
        fiscal_year: 2027,
        department,
        current_headcount: Number(currentHeadcount),
        target_headcount: Number(targetHeadcount),
        approved_budget_usd: Number(budgetUsd),
        projected_attrition_rate: 0.08,
      });
      await loadData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading AI Workforce Planning & Headcount Models...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-indigo-400" />
          AI Workforce Planning & Headcount Forecasting
        </h2>
        <p className="text-sm text-slate-400">
          Model departmental hiring budgets (1.28x fully-loaded cost), simulate attrition backfills, and sync approved requisitions to ai-recruiter.
        </p>
      </div>

      {error && <div className="bg-red-950/60 border border-red-500/40 text-red-200 px-4 py-3 rounded-lg text-sm">{error}</div>}
      {syncMessage && (
        <div className="bg-emerald-950/60 border border-emerald-500/40 text-emerald-200 px-4 py-3 rounded-lg text-sm">
          {syncMessage}
        </div>
      )}

      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
            <div className="text-xs text-slate-400 flex items-center gap-1">
              <Users className="w-3.5 h-3.5" /> Current → Target Headcount
            </div>
            <div className="text-2xl font-bold text-white mt-1">
              {summary.total_current_headcount} → {summary.total_target_headcount}
            </div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
            <div className="text-xs text-slate-400 flex items-center gap-1">
              <DollarSign className="w-3.5 h-3.5" /> Approved Hiring Budget
            </div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">
              ${(summary.total_approved_budget_usd / 1_000_000).toFixed(2)}M
            </div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
            <div className="text-xs text-slate-400">Planned Requisitions</div>
            <div className="text-2xl font-bold text-white mt-1">{summary.total_open_requisitions}</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
            <div className="text-xs text-slate-400">Synced to ai-recruiter</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{summary.synced_to_recruiter_count}</div>
          </div>
        </div>
      )}

      {simulation && (
        <div className="bg-indigo-950/50 border border-indigo-500/40 rounded-xl p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-indigo-300 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4" /> {simulation.department} — {simulation.scenario} Scenario Simulation
            </span>
            <span className={`text-xs font-mono ${simulation.budget_variance_usd >= 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
              Budget Variance: ${simulation.budget_variance_usd.toLocaleString()}
            </span>
          </div>
          <p className="text-sm text-slate-200">{simulation.ai_recommendation}</p>
          <div className="flex flex-wrap gap-4 text-xs text-slate-300 pt-1">
            <span>Net-New: {simulation.net_new_hires}</span>
            <span>Backfills: {simulation.attrition_backfills}</span>
            <span>Total Hires: {simulation.total_hiring_need}</span>
            <span>Fully-Loaded Cost: ${simulation.estimated_total_fully_loaded_cost.toLocaleString()}</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {plans.map((plan) => (
            <div key={plan.id} className="bg-slate-800 border border-slate-700 rounded-xl p-5 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <h3 className="text-lg font-semibold text-white">
                    {plan.department} (FY{plan.fiscal_year})
                  </h3>
                  <p className="text-xs text-slate-400">{plan.ai_rationale}</p>
                </div>
                <div className="flex gap-1.5">
                  {(['CONSERVATIVE', 'BASELINE', 'HYPERGROWTH'] as const).map((sc) => (
                    <button
                      key={sc}
                      onClick={() => handleSimulate(plan.id, sc)}
                      className="px-2.5 py-1 bg-slate-900 hover:bg-indigo-600 text-slate-200 text-[11px] font-medium rounded border border-slate-700"
                    >
                      {sc}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                {plan.requisitions.map((req) => (
                  <div
                    key={req.id}
                    className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 bg-slate-900 border border-slate-700 rounded-lg px-3.5 py-2.5"
                  >
                    <div>
                      <div className="text-sm font-medium text-white">
                        {req.role_title} <span className="text-xs text-indigo-400 font-mono">({req.job_level})</span>
                      </div>
                      <div className="text-xs text-slate-400">
                        {req.target_quarter} | Base: ${req.estimated_base_salary.toLocaleString()} | Loaded (1.28x): $
                        {req.fully_loaded_cost.toLocaleString()}
                      </div>
                    </div>
                    {req.recruiter_sync_status === 'SYNCED_TO_RECRUITER' ? (
                      <span className="px-2.5 py-1 bg-emerald-500/20 text-emerald-300 text-xs font-mono rounded">
                        SYNCED_TO_RECRUITER
                      </span>
                    ) : (
                      <button
                        onClick={() => handleSyncRecruiter(req.id)}
                        className="inline-flex items-center gap-1 px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded"
                      >
                        <Send className="w-3 h-3" /> Sync to ai-recruiter
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <form onSubmit={handleCreatePlan} className="bg-slate-800 border border-slate-700 rounded-xl p-5 space-y-4 h-fit">
          <h3 className="text-lg font-semibold text-white">Create Department Plan</h3>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Department</label>
            <input
              type="text"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              required
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Current HC</label>
              <input
                type="number"
                value={currentHeadcount}
                onChange={(e) => setCurrentHeadcount(Number(e.target.value))}
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Target HC</label>
              <input
                type="number"
                value={targetHeadcount}
                onChange={(e) => setTargetHeadcount(Number(e.target.value))}
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Approved Budget (USD)</label>
            <input
              type="number"
              value={budgetUsd}
              onChange={(e) => setBudgetUsd(Number(e.target.value))}
              required
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
            />
          </div>
          <button
            type="submit"
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg"
          >
            Create FY2027 Plan
          </button>
        </form>
      </div>
    </div>
  );
};
