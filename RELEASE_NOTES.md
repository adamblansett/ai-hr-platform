# Release v1.0.0 — `ai-hr-platform`

**Release Date:** November 18, 2026  
**License:** Apache 2.0  
**Status:** Production Ready  

`ai-hr-platform` is an independently deployable open-source microservice engineered to automate core enterprise human resource operations, employee onboarding, digital compliance checklists, leave management, grounded policy RAG Q&A, and continuous performance reviews.

---

## 🌟 Key Highlights & Architecture

### 1. Foundation Capabilities (Milestones 01–17)
- **Monorepo Layout:** Unified Python FastAPI backend, React 18 / Vite / TypeScript frontend, Docker Compose stack, and production documentation.
- **Async Relational Database & pgvector:** SQLAlchemy 2.0 asyncpg engine with Alembic migrations, supporting dual-vector indexing (768-dim local open models + 1536-dim cloud models) with HNSW indexes.
- **Multi-Tenant Security & RBAC:** Multi-tenant organization scoping, bcrypt password security, dual-token JWT lifecycle, and role-based guards (`SUPER_ADMIN`, `HR_ADMIN`, `PEOPLE_MANAGER`, `EMPLOYEE`).
- **Upstream Recruitment Integration:** HMAC-SHA256 verified webhook (`POST /api/v1/webhooks/recruiter/offer-accepted`) for instant candidate-to-employee handoff from `ai-recruiter`.
- **Automated Onboarding Engine:** Role-specific task checklist generation, compliance tracking, and automated status transitions to `ACTIVE` upon 100% completion.
- **Policy Enforcement & Grounded RAG Assistant:** Semantic chunking engine with cited clause retrieval (`POST /api/v1/policies/chat`) and cryptographic SHA-256 digital signature acknowledgment.
- **Leave Management & Team Conflict Detection:** Multi-tier policies (PTO, Sick, Parental), working-day calculators, and departmental calendar overlap conflict detection.
- **360-Degree Performance Reviews:** Review cycle orchestration, OKR/goal tracking, and unbiased AI review synthesis using structured Pydantic models.
- **Zero-Leak PII Scrubber:** High-throughput regex scrubber masking SSNs, credit cards, dates of birth, personal emails, and phone numbers before LLM inference.
- **CI/CD Pipeline:** GitHub Actions workflow testing backend on PostgreSQL 16 + Redis and building frontend assets.

---

### 2. Phase 2 Enterprise Integrations
- **Conversational Chatbot (Slack & MS Teams):**
  - Slash command `/ask-hr <question>` for conversational handbook Q&A.
  - Interactive Slack Block Kit & Teams Adaptive Cards for one-click manager leave approvals.
- **Inbound SCIM 2.0 Server (`/api/v1/scim/v2`):** RFC 7643 & RFC 7644 implementation for inbound user provisioning and deactivation from Okta, Microsoft Entra ID (Azure AD), and OneLogin.
- **Automated Document OCR & Verification:** Form classifier and signature detection engine for digital onboarding uploads (I-9, W-4, Direct Deposit).
- **Cloud-Native Kubernetes Helm Chart:** Complete chart in `deploy/helm/ai-hr-platform` with CPU-based HPA auto-scaling (3 to 10 replicas) and cert-manager Ingress.
- **HR Analytics & Calibration:** Executive dashboards for headcount, onboarding completion rates, leave utilization, and departmental OKR progress.

---

### 3. Operational Tooling Included
- **Database Seeder (`backend/app/scripts/seed.py`):** Seeds default Acme Innovations tenant, 4 demo roles, leave policies, and pre-vectorized policy documents.
- **Simulation CLI (`backend/scripts/simulate_recruiter_handoff.py`):** Standalone tool to simulate and verify recruitment webhooks.
- **API Collection (`docs/api_collection.json`):** Full Postman v2.1.0 collection with pre-authenticated demo requests.
- **Playwright E2E Suite (`frontend/tests/e2e/`):** Automated browser tests covering authentication, onboarding, policy Q&A, and leave submission.

---

## 🚀 Quickstart Deployment

```bash
# 1. Clone repository
git clone https://github.com/adamblansett/ai-hr-platform.git
cd ai-hr-platform

# 2. Launch stack via Docker Compose
docker compose -f docker/docker-compose.yml up -d --build

# 3. Seed demo data
docker exec -it ai_hr_backend python -m backend.app.scripts.seed

# 4. Access Portal
# Unified Ingress:   http://localhost
# API Documentation: http://localhost:8000/api/v1/docs
# Telemetry Metrics: http://localhost:8000/metrics
```

Demo Credentials:
- **HR Admin:** `admin@acme.corp` / `Password123!`
- **Manager:** `manager.sarah@acme.corp` / `Password123!`
- **Engineer:** `engineer.alex@acme.corp` / `Password123!`
- **New Hire:** `newhire.elena@acme.corp` / `Password123!`
