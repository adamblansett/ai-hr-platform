# 17-Milestone Execution Roadmap: `ai-hr-platform`

This roadmap provides an actionable, sequential execution plan for developing, testing, and shipping `ai-hr-platform` from day zero through enterprise production readiness.

---

### Milestone 01: Repository Bootstrap, Monorepo Scaffolding & Tooling [COMPLETED]
- **Objective:** Establish the production monorepo structure, dev container tooling, linting, formatting, and Docker Compose orchestration.
- **Key Deliverables:**
  - Standardized monorepo layout (`/backend`, `/frontend`, `/docker`, `/docs`).
  - Pre-commit configurations (`ruff`, `mypy`, `black`, `eslint`, `prettier`).
  - Docker Compose stack with PostgreSQL 16 + pgvector, Redis 7, Ollama, backend, and frontend.
- **Technical Specs:** Python 3.12, Node 20+, Docker Compose v2.
- **Status:** Complete.

---

### Milestone 02: Multi-Tenant Database Schema, Migrations & pgvector Setup [COMPLETED]
- **Objective:** Initialize the PostgreSQL relational schema with `pgvector` vector extension, foreign keys, and Alembic async migration pipeline.
- **Key Deliverables:**
  - Alembic configuration supporting asyncpg and UUID/Vector types (`alembic.ini`, `backend/alembic/env.py`).
  - Initial migration scripts for `organizations`, `employees`, `onboarding_tasks`, `policy_documents`, `leave_requests`, `performance_cycles`, and `audit_logs` (`0001_initial_schema.py`).
  - Multi-tenant tenant-scoping baseline mixins and indexes.
- **Technical Specs:** SQLAlchemy 2.0 (async), Alembic, pgvector.
- **Status:** Complete.

---

### Milestone 03: Authentication, JWT Token Lifecycle & RBAC Middleware [COMPLETED]
- **Objective:** Implement tenant-aware authentication, secure password hashing, refresh token rotation, and Role-Based Access Control (RBAC).
- **Key Deliverables:**
  - Endpoints: `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `GET /api/v1/auth/me`.
  - Dependency injectors: `get_current_user`, `require_role(["HR_ADMIN", "SUPER_ADMIN"])`.
  - Security primitives: password hashing via bcrypt, access and refresh JWT creation and decoding.
- **Technical Specs:** JWT (HS256 or RS256), Passlib (bcrypt), FastAPI Security HTTPBearer.
- **Status:** Complete.

---

### Milestone 04: Employee Records, Directory & Profile Management API [COMPLETED]
- **Objective:** Build centralized CRUD endpoints for managing employee directories, departmental hierarchies, and managerial reporting trees.
- **Key Deliverables:**
  - Endpoints: `GET /api/v1/employees`, `POST /api/v1/employees`, `GET /api/v1/employees/{id}`, `PATCH /api/v1/employees/{id}`.
  - Self-service endpoints: `GET /api/v1/employees/me`, `PATCH /api/v1/employees/me`.
  - Org-chart recursive tree traversal endpoint `GET /api/v1/employees/org-chart`.
- **Technical Specs:** Pydantic v2 schemas with strict field masking, async pagination, query filters by department/status.
- **Status:** Complete.

---

### Milestone 05: Upstream `ai-recruiter` Webhook Ingestion & Candidate Handoff [COMPLETED]
- **Objective:** Provide a secure webhook ingress point for `ai-recruiter` upon candidate offer acceptance to transition candidate records into onboarding stubs.
- **Key Deliverables:**
  - Endpoint: `POST /api/v1/webhooks/recruiter/offer-accepted`.
  - HMAC-SHA256 signature verification middleware.
  - Atomic transaction creating the employee in status `ONBOARDING`, generating initial onboarding task checklist, dispatching IdP provisioning, and recording audit logs.
- **Technical Specs:** FastAPI raw request body hashing, Celery background worker event trigger.
- **Status:** Complete.

---

### Milestone 06: Automated Onboarding Workflows & Task Orchestration [COMPLETED]
- **Objective:** Construct an onboarding engine that generates default role/department onboarding checklists, dispatches IdP provisioning actions (Mock Adapter, SCIM 2.0 / Okta, or Google Workspace), and tracks progress.
- **Key Deliverables:**
  - Template engine for onboarding workflows (IT equipment, paperwork, security training).
  - Pluggable IdP provisioning pipeline supporting `MockProvisioningAdapter`, `SCIMProvisioningAdapter` (Okta), and `GoogleWorkspaceProvisioningAdapter`.
  - Endpoints: `GET /api/v1/onboarding/tasks`, `PATCH /api/v1/onboarding/tasks/{id}`, `GET /api/v1/onboarding/me/progress`.
  - Celery task scheduler sending reminders for approaching task deadlines (`backend/app/workers/onboarding_tasks.py`).
- **Technical Specs:** Celery 5.4, Redis, RFC 7643/7644 SCIM 2.0, Google Admin SDK.
- **Status:** Complete.

---

### Milestone 07: Document Collection & Digital Compliance Checklists [COMPLETED]
- **Objective:** Enable secure uploading, verification, and digital signing of compliance documents (I-9, W-4, direct deposit, emergency contacts).
- **Key Deliverables:**
  - Secure document attachment endpoint: `POST /api/v1/onboarding/tasks/{id}/upload-document`.
  - Document status tracking (`UPLOADED_PENDING_HR_VERIFICATION`).
  - Cryptographic signature generation and verification.
- **Technical Specs:** SHA256 file hashing, MIME-type validation.
- **Status:** Complete.

---

### Milestone 08: Provider-Agnostic LLM Inference Router & Fallback Mechanism [COMPLETED]
- **Objective:** Architect a flexible inference router connecting local Ollama instances with cloud fallback providers, supporting seamless model switching.
- **Key Deliverables:**
  - Adapter implementation for Ollama (`llama3.1:8b`, `qwen2.5:7b`, `mistral-nemo:12b`) and OpenAI (`gpt-4o-mini`).
  - Structured Pydantic JSON parsing with `complete_structured(...)`.
  - Defensive prompt injection sanitization.
- **Technical Specs:** HTTPX async client, tenacity retries, Ollama REST API.
- **Status:** Complete.

---

### Milestone 09: Zero-Leak PII Redaction & Immutable Audit Logging Pipeline [COMPLETED]
- **Objective:** Protect employee confidential data by stripping PII before LLM calls and recording an immutable audit trail for all administrative mutations.
- **Key Deliverables:**
  - High-throughput regex & NER-based `PIIScrubber` service (SSN, credit card, phone, personal email, DOB).
  - Centralized audit service: `backend/app/services/audit_service.py`.
  - Admin audit inquiry API: `GET /api/v1/audit-logs`.
- **Technical Specs:** PostgreSQL JSONB columns, async logging tasks.
- **Status:** Complete.

---

### Milestone 10: Policy Knowledge Base Ingestion & Semantic Chunking Engine [COMPLETED]
- **Objective:** Provide automated ingestion and chunking of employee handbooks, labor regulations, and corporate SOPs into dual vector embeddings (768-dim and 1536-dim).
- **Key Deliverables:**
  - Ingestion endpoint: `POST /api/v1/policies/upload`.
  - Recursive chunking engine (1200 chars, 150 char overlap) preserving paragraph boundaries.
  - Dual vector generation via `EmbeddingService`: 768-dim (`nomic-embed-text` / `bge-base`) and 1536-dim (`text-embedding-3-small`), persisted to `pgvector`.
- **Technical Specs:** PostgreSQL HNSW index on `policy_documents.embedding_768` and `embedding_1536`.
- **Status:** Complete.

---

### Milestone 11: RAG Q&A Engine with Cited Evidence & Acknowledgment Tracking [COMPLETED]
- **Objective:** Implement the employee self-service AI assistant for policy Q&A with strict grounding and source citations, plus digital policy acknowledgment.
- **Key Deliverables:**
  - Grounded RAG endpoint: `POST /api/v1/policies/chat` returning answers with paragraph citations and cosine relevance scores.
  - Policy acknowledgment endpoints: `POST /api/v1/policies/{id}/acknowledge` and `GET /api/v1/policies/{id}/acknowledgments`.
  - Cryptographic SHA256 digital signature tracking.
- **Technical Specs:** Semantic retrieval augmented generation (RAG) with tenant filter.
- **Status:** Complete.

---

### Milestone 12: Leave & Attendance Policy Engine, Accruals & Balance Tracking [COMPLETED]
- **Objective:** Configure multi-tier leave policies (PTO, Sick, Parental, Bereavement) with automated monthly accruals, rollover caps, and balance calculations.
- **Key Deliverables:**
  - Endpoints: `POST /api/v1/leave/policies`, `GET /api/v1/leave/policies`, `GET /api/v1/leave/balances/me`.
  - Accrual calculation and balance tracking service: `backend/app/services/leave_service.py`.
  - Business day calculator excluding weekends.
- **Technical Specs:** Transaction-safe balance updates.
- **Status:** Complete.

---

### Milestone 13: Leave Request Routing & Calendar Conflict Detection Service [COMPLETED]
- **Objective:** Deliver self-service leave submission, managerial approval workflows, and automated calendar conflict detection.
- **Key Deliverables:**
  - Endpoints: `POST /api/v1/leave/requests`, `GET /api/v1/leave/requests/me`, `GET /api/v1/leave/requests/pending`, `PATCH /api/v1/leave/requests/{id}/decision`.
  - Conflict detection service checking concurrent leave requests across the same department.
  - Audit logging on approval/rejection.
- **Technical Specs:** Date range overlap SQL queries.
- **Status:** Complete.

---

### Milestone 14: Performance Review Cycles & OKR/Goal Tracking Engine [COMPLETED]
- **Objective:** Build enterprise performance management tools for scheduling review cycles, cascading OKRs, and tracking goal progress.
- **Key Deliverables:**
  - Cycle orchestration: `POST /api/v1/performance/cycles`, `GET /api/v1/performance/cycles`.
  - OKR tracking endpoints: `POST /api/v1/performance/goals`, `PATCH /api/v1/performance/goals/{id}`, `GET /api/v1/performance/goals/me`.
  - Automatic status updates upon 100% completion.
- **Technical Specs:** PostgreSQL JSONB for flexible rubric definitions.
- **Status:** Complete.

---

### Milestone 15: 360-Degree Feedback Synthesis & AI-Assisted Review Drafting [COMPLETED]
- **Objective:** Facilitate peer, self, and manager reviews, synthesizing diverse multi-perspective feedback into balanced, objective AI-assisted summaries.
- **Key Deliverables:**
  - Endpoints: `POST /api/v1/performance/reviews`, `POST /api/v1/performance/reviews/synthesize`.
  - Unbiased LLM synthesis prompt reducing subjectivity and extracting key strengths & growth opportunities.
- **Technical Specs:** LLM Router structured schema generation.
- **Status:** Complete.

---

### Milestone 16: React/Vite Frontend Self-Service Portal & HR Admin Dashboard [COMPLETED]
- **Objective:** Build a responsive, accessible React/TypeScript single-page application for employee self-service and HR administration.
- **Key Deliverables:**
  - API Client with JWT bearer management: `frontend/src/services/api.ts`.
  - Views: Onboarding Checklist, Policy Assistant Q&A, Leave & PTO Management, Employee Directory, and Auth modal.
  - Tailwind CSS dark-mode theme.
- **Technical Specs:** Vite, React 18, TypeScript, Tailwind CSS.
- **Status:** Complete.

---

### Milestone 17: End-to-End Integration Testing, Security Audits & Production Deployment [COMPLETED]
- **Objective:** Perform end-to-end integration tests, security audits, OpenAPI documentation validation, and production CI/CD deployment configuration.
- **Key Deliverables:**
  - Unit & security test suite: `backend/tests/test_auth.py`, `backend/tests/test_webhooks.py`, `backend/tests/test_pii_scrubber.py`.
  - GitHub Actions CI/CD workflow: `.github/workflows/ci.yml`.
  - Multi-container Docker Compose configuration: `docker/docker-compose.yml`.
- **Technical Specs:** Pytest, GitHub Actions, Docker multi-stage builds.
- **Status:** Complete.
