import os
import uuid
from datetime import date
import pytest

httpx = pytest.importorskip("httpx")
fastapi = pytest.importorskip("fastapi")

from httpx import ASGITransport, AsyncClient
from backend.app.main import app


@pytest.mark.asyncio
async def test_health_metrics_security_headers_and_v21_routes():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Health & Live probes + Correlation ID + Security headers
        health_res = await client.get("/health", headers={"X-Request-ID": "ci-req-001"})
        assert health_res.status_code == 200
        assert health_res.json()["version"] == "2.1.0"
        assert health_res.headers.get("X-Request-ID") == "ci-req-001"
        assert health_res.headers.get("X-Content-Type-Options") == "nosniff"
        assert health_res.headers.get("X-Frame-Options") == "DENY"

        live_res = await client.get("/health/live")
        assert live_res.status_code == 200
        assert live_res.json()["status"] == "alive"

        # 2. Prometheus exposition metrics
        metrics_res = await client.get("/metrics")
        assert metrics_res.status_code == 200
        assert "ai_hr_http_requests_total" in metrics_res.text

        # 3. v2.1 New Feature Endpoints
        sso_res = await client.get("/api/v1/security/sso/providers")
        assert sso_res.status_code == 200
        assert len(sso_res.json()) >= 2

        notif_res = await client.get("/api/v1/notifications/me")
        assert notif_res.status_code == 200
        assert len(notif_res.json()) >= 1

        wfp_res = await client.get("/api/v1/workforce-planning/summary")
        assert wfp_res.status_code == 200
        assert wfp_res.json()["total_plans"] >= 2


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.getenv("RUN_DB_INTEGRATION_TESTS") != "true",
    reason="Requires live PostgreSQL and Redis (enabled in CI)",
)
async def test_e2e_db_readiness_auth_rotation_logout_rbac_and_tenant_isolation():
    from backend.app.core.database import AsyncSessionLocal, engine
    from backend.app.core.security import get_password_hash
    from backend.app.models.employee import Employee, EmployeeRole, EmploymentStatus, EmploymentType
    from backend.app.models.organization import Organization

    org_a_id = uuid.uuid4()
    org_b_id = uuid.uuid4()
    suffix = uuid.uuid4().hex[:6]
    admin_email = f"admin-{suffix}@orga.test"
    emp_a_email = f"emp-{suffix}@orga.test"
    emp_b_email = f"emp-{suffix}@orgb.test"
    password = "TestPassword123!"

    try:
        async with AsyncSessionLocal() as session:
            org_a = Organization(id=org_a_id, name="Tenant Alpha", slug=f"alpha-{suffix}", domain=f"alpha-{suffix}.local")
            org_b = Organization(id=org_b_id, name="Tenant Beta", slug=f"beta-{suffix}", domain=f"beta-{suffix}.local")
            session.add_all([org_a, org_b])
            await session.flush()

            pw_hash = get_password_hash(password)
            admin_a = Employee(
                organization_id=org_a_id,
                email=admin_email,
                hashed_password=pw_hash,
                first_name="Alice",
                last_name="Admin",
                role=EmployeeRole.HR_ADMIN,
                status=EmploymentStatus.ACTIVE,
                employment_type=EmploymentType.FULL_TIME,
                department="People",
                job_title="VP People",
                hire_date=date(2025, 1, 10),
            )
            emp_a = Employee(
                organization_id=org_a_id,
                email=emp_a_email,
                hashed_password=pw_hash,
                first_name="Bob",
                last_name="Builder",
                role=EmployeeRole.EMPLOYEE,
                status=EmploymentStatus.ACTIVE,
                employment_type=EmploymentType.FULL_TIME,
                department="Engineering",
                job_title="Engineer",
                hire_date=date(2025, 2, 1),
            )
            emp_b = Employee(
                organization_id=org_b_id,
                email=emp_b_email,
                hashed_password=pw_hash,
                first_name="Charlie",
                last_name="TenantB",
                role=EmployeeRole.HR_ADMIN,
                status=EmploymentStatus.ACTIVE,
                employment_type=EmploymentType.FULL_TIME,
                department="Sales",
                job_title="Director",
                hire_date=date(2025, 3, 1),
            )
            session.add_all([admin_a, emp_a, emp_b])
            await session.commit()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Live PostgreSQL & Redis Readiness Check
            ready_res = await client.get("/health/ready")
            assert ready_res.status_code == 200
            assert ready_res.json()["checks"] == {"postgres": "ok", "redis": "ok"}

            # 2. Authenticate Admin in Tenant A -> verify /me
            login_res = await client.post("/api/v1/auth/login", json={"email": admin_email, "password": password})
            assert login_res.status_code == 200
            tokens = login_res.json()
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]

            me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
            assert me_res.status_code == 200
            assert me_res.json()["organization_id"] == str(org_a_id)

            # 3. Cross-Tenant Isolation: Org A Admin only sees Org A employees, never Org B
            list_res = await client.get("/api/v1/employees/", headers={"Authorization": f"Bearer {access_token}"})
            assert list_res.status_code == 200
            emails_visible = {item["email"] for item in list_res.json()["items"]}
            assert admin_email in emails_visible
            assert emp_a_email in emails_visible
            assert emp_b_email not in emails_visible

            # 4. Refresh Token Rotation + Replay Rejection
            rot_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
            assert rot_res.status_code == 200
            rotated_tokens = rot_res.json()
            assert rotated_tokens["refresh_token"] != refresh_token

            replay_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
            assert replay_res.status_code == 401

            # 5. Logout revokes active access + refresh tokens immediately
            logout_res = await client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": rotated_tokens["refresh_token"]},
                headers={"Authorization": f"Bearer {rotated_tokens['access_token']}"},
            )
            assert logout_res.status_code == 200
            assert logout_res.json()["revoked_tokens"] == 2

            revoked_me = await client.get(
                "/api/v1/auth/me", headers={"Authorization": f"Bearer {rotated_tokens['access_token']}"}
            )
            assert revoked_me.status_code == 401

            # 6. RBAC Enforcement: EMPLOYEE role receives 403 on admin-only endpoints
            emp_login = await client.post("/api/v1/auth/login", json={"email": emp_a_email, "password": password})
            assert emp_login.status_code == 200
            emp_token = emp_login.json()["access_token"]

            forbidden_sso = await client.post(
                "/api/v1/security/sso/providers",
                json={
                    "provider_type": "OIDC",
                    "provider_name": "Unauthorized IdP",
                    "issuer_url": "https://evil.example.com",
                    "sso_login_url": "https://evil.example.com/auth",
                },
                headers={"Authorization": f"Bearer {emp_token}"},
            )
            assert forbidden_sso.status_code == 403
    finally:
        await engine.dispose()
