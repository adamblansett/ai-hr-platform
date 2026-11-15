# 17-Milestone Execution Roadmap: `ai-hr-platform`

This roadmap provides an actionable, sequential execution plan for developing, testing, and shipping `ai-hr-platform` from day zero through enterprise production readiness.

---

### Milestone 01: Repository Bootstrap, Monorepo Scaffolding & Tooling
- **Objective:** Establish the production monorepo structure, dev container tooling, linting, formatting, and Docker Compose orchestration.
- **Key Deliverables:**
  - Standardized monorepo layout (`/backend`, `/frontend`, `/docker`, `/docs`).
  - Pre-commit configurations (`ruff`, `mypy`, `black`, `eslint`, `prettier`).
  - Docker Compose stack with PostgreSQL 16 + pgvector, Redis 7, Ollama, backend, and frontend.
- **Technical Specs:** Python 3.12, Node 20+, Docker Compose v2.
- **Acceptance Criteria:** `docker compose -f docker/docker-compose.yml up -d` boots all services without errors; `/health` returns status `healthy`.

---

### Milestone 02: Multi-Tenant Database Schema, Migrations & pgvector Setup
- **Objective:** Initialize the PostgreSQL relational schema with `pgvector` vector extension, foreign keys, and Alembic async migration pipeline.
- **Key Deliverables:**
  - Alembic configuration supporting asyncpg and UUID/Vector types.
  - Initial migration scripts for `organizations`, `employees`, `onboarding_tasks`, `policy_documents`, `leave_requests`, `performance_cycles`, and `audit_logs`.
  - Multi-tenant tenant-scoping baseline mixins and indexes.
- **Technical Specs:** SQLAlchemy 2.0 (async), Alembic, pgvector.
- **Acceptance Criteria:** Migrations run cleanly up and down; `pgvector` extension is verified active in PostgreSQL with vector dimension testing.

---

### Milestone 03: Authentication, JWT Token Lifecycle & RBAC Middleware
- **Objective:** Implement tenant-aware authentication, secure password hashing, refresh token rotation, and Role-Based Access Control (RBAC).
- **Key Deliverables:**
  - Endpoints: `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`.
  - Dependency injectors: `get_current_user`, `require_role(["HR_ADMIN", "SUPER_ADMIN"])`.
  - Multi-tenant middleware injecting `organization_id` into database session query scopes.
- **Technical Specs:** JWT (HS256 or RS256), Passlib (bcrypt), FastAPI Security OAuth2PasswordBearer.
- **Acceptance Criteria:** Employees can authenticate; unauthorized cross-tenant data access attempts return `403 Forbidden` or `404 Not Found`.

---

### Milestone 04: Employee Records, Directory & Profile Management API
- **Objective:** Build centralized CRUD endpoints for managing employee directories, departmental hierarchies, and managerial reporting trees.
- **Key Deliverables:**
  - Endpoints: `GET /api/v1/employees`, `POST /api/v1/employees`, `GET /api/v1/employees/{id}`, `PATCH /api/v1/employees/{id}`.
  - Self-service endpoints: `GET /api/v1/employees/me`, `PATCH /api/v1/employees/me`.
  - Org-chart recursive tree traversal endpoint `GET /api/v1/employees/org-chart`.
- **Technical Specs:** Pydantic v2 schemas with strict field masking, async pagination, query filters by department/status.
- **Acceptance Criteria:** Employee profile management respects RBAC (managers see direct reports; employees edit only whitelisted self-fields).

---

### Milestone 05: Upstream `ai-recruiter` Webhook Ingestion & Candidate Handoff
- **Objective:** Provide a secure webhook ingress point for `ai-recruiter` upon candidate offer acceptance to transition candidate records into onboarding stubs.
- **Key Deliverables:**
  - Endpoint: `POST /api/v1/webhooks/recruiter/offer-accepted`.
  - HMAC-SHA256 signature verification middleware.
  - Atomic transaction creating the employee in status `ONBOARDING` and dispatching initial welcome credentials.
- **Technical Specs:** FastAPI raw request body hashing, Celery background worker event trigger.
- **Acceptance Criteria:** Valid signed payloads create an employee with candidate ID cross-reference; invalid signatures are rejected with `401 Unauthorized`.

---

### Milestone 06: Automated Onboarding Workflows & Task Orchestration
- **Objective:** Construct an onboarding engine that generates default role/department onboarding checklists, dispatches IdP provisioning actions (Mock Adapter, SCIM 2.0 / Okta, or Google Workspace), and tracks progress.
- **Key Deliverables:**
  - Template engine for onboarding workflows (IT equipment, paperwork, security training).
  - Pluggable IdP provisioning pipeline supporting `MockProvisioningAdapter`, `SCIMProvisioningAdapter` (Okta), and `GoogleWorkspaceProvisioningAdapter`.
  - Endpoints: `GET /api/v1/onboarding/tasks`, `PATCH /api/v1/onboarding/tasks/{id}/status`, `POST /api/v1/onboarding/provision/{employee_id}`.
  - Celery task scheduler sending reminders for approaching task deadlines.
- **Technical Specs:** Celery 5.4, Redis, RFC 7643/7644 SCIM 2.0, Google Admin SDK.
- **Acceptance Criteria:** When an employee enters `ONBOARDING`, template tasks are spawned and IdP accounts are provisioned via the configured adapter.

---

### Milestone 07: Document Collection & Digital Compliance Checklists
- **Objective:** Enable secure uploading, verification, and digital signing of compliance documents (I-9, W-4, direct deposit, emergency contacts).
- **Key Deliverables:**
  - Secure S3 / local minio file upload endpoint with presigned URLs.
  - Document status tracking (`PENDING_UPLOAD`, `PENDING_REVIEW`, `VERIFIED`, `REJECTED`).
  - Cryptographic signature generation and verification.
- **Technical Specs:** Presigned S3 URLs, SHA256 file hashing, MIME-type validation.
- **Acceptance Criteria:** Employees upload required compliance documents; HR admins can approve or reject with audit trail recording.

---

### Milestone 08: Provider-Agnostic LLM Inference Router & Fallback Mechanism
- **Objective:** Architect a flexible inference router connecting local Ollama instances with cloud fallback providers, supporting seamless model switching.
- **Key Deliverables:**
  - Adapter pattern implementation for Ollama (`llama3.1:8b`, `qwen2.5:7b`, `mistral-nemo:12b`), OpenAI (`gpt-4o-mini`), and Anthropic.
  - Resilient retry loop with exponential backoff and circuit-breaker patterns.
  - Structured JSON output parsing and prompt templating utilities.
- **Technical Specs:** HTTPX async client, tenacity retries, Ollama REST API.
- **Acceptance Criteria:** Requests dynamically route to local Ollama; if Ollama is unreachable, gracefully fall back to cloud API with telemetry metrics.

---

### Milestone 09: Zero-Leak PII Redaction & Immutable Audit Logging Pipeline
- **Objective:** Protect employee confidential data by stripping PII before LLM calls and recording an immutable audit trail for all administrative mutations.
- **Key Deliverables:**
  - High-throughput regex & NER-based `PIIScrubber` service (SSN, credit card, phone, personal email, DOB).
  - Async audit log decorator `@audit_event(action, entity_type)`.
  - Admin audit inquiry API: `GET /api/v1/audit-logs`.
- **Technical Specs:** PostgreSQL JSONB columns, async logging tasks via Celery to avoid latency in user-facing endpoints.
- **Acceptance Criteria:** PII is proven redacted in LLM request logs and audit records; admin actions generate queryable audit logs.

---

### Milestone 10: Policy Knowledge Base Ingestion & Semantic Chunking Engine
- **Objective:** Provide automated ingestion and chunking of employee handbooks, labor regulations, and corporate SOPs into dual vector embeddings (768-dim and 1536-dim).
- **Key Deliverables:**
  - Upload endpoints for PDF, DOCX, and Markdown files: `POST /api/v1/policies/upload`.
  - Recursive chunking engine (750 tokens, 100-token overlap) with header hierarchy retention.
  - Dual vector generation via `EmbeddingService`: 768-dim (`nomic-embed-text` / `bge-base`) and 1536-dim (`text-embedding-3-small`), persisted to `pgvector`.
- **Technical Specs:** LangChain/LlamaIndex chunking splitters or custom async tokenizer, PostgreSQL HNSW index on `policy_documents.embedding_768` and `embedding_1536`.
- **Acceptance Criteria:** Ingested documents produce vector embeddings in PostgreSQL; cosine similarity search retrieves relevant paragraphs in <25ms across both dimensions.

---

### Milestone 11: RAG Q&A Engine with Cited Evidence & Acknowledgment Tracking
- **Objective:** Implement the employee self-service AI assistant for policy Q&A with strict grounding and source citations, plus digital policy acknowledgment.
- **Key Deliverables:**
  - Endpoint: `POST /api/v1/policies/chat` returning answers with paragraph citations `[Policy: Handbook v2, Sec 4.2]`.
  - Policy acknowledgment endpoints: `POST /api/v1/policies/{id}/acknowledge`.
  - HR compliance compliance matrix showing signed vs delinquent employees.
- **Technical Specs:** Semantic retrieval augmented generation (RAG) with tenant filter, prompt guardrails against hallucinations.
- **Acceptance Criteria:** Model answers only using ingested context; hallucination attempts return "Information not found in company policy"; acknowledgments are tracked.

---

### Milestone 12: Leave & Attendance Policy Engine, Accruals & Balance Tracking
- **Objective:** Configure multi-tier leave policies (PTO, Sick, Parental, Bereavement) with automated monthly accruals, rollover caps, and balance calculations.
- **Key Deliverables:**
  - Endpoints: `POST /api/v1/leave/policies`, `GET /api/v1/leave/balances/me`.
  - Scheduled Celery Beat task running end-of-month accruals and annual rollover adjustments.
  - Manual adjustment API for HR admins with required audit justification.
- **Technical Specs:** Precise floating-point / decimal arithmetic, transaction-safe balance updates.
- **Acceptance Criteria:** Monthly Celery job accurately increments employee leave balances up to defined policy caps.

---

### Milestone 13: Leave Request Routing & Calendar Conflict Detection Service
- **Objective:** Deliver self-service leave submission, managerial approval workflows, and automated calendar conflict detection.
- **Key Deliverables:**
  - Endpoints: `POST /api/v1/leave/requests`, `PATCH /api/v1/leave/requests/{id}/decision`.
  - Conflict detection service checking concurrent leave requests across the same department or project team.
  - Email / notification webhook dispatch to approving managers.
- **Technical Specs:** Date range overlap SQL queries, Celery notification dispatch.
- **Acceptance Criteria:** Submitting leave checks for team overlap, flags conflicts for manager review, and decrements balances upon approval.

---

### Milestone 14: Performance Review Cycles & OKR/Goal Tracking Engine
- **Objective:** Build enterprise performance management tools for scheduling review cycles, cascading OKRs, and tracking goal progress.
- **Key Deliverables:**
  - Cycle orchestration: `POST /api/v1/performance/cycles`, `GET /api/v1/performance/cycles/active`.
  - OKR tracking endpoints: `POST /api/v1/performance/goals`, `PATCH /api/v1/performance/goals/{id}/progress`.
  - Automated phase transitions (`UPCOMING` -> `ACTIVE` -> `EVALUATION` -> `CLOSED`).
- **Technical Specs:** PostgreSQL JSONB for flexible rubric definitions, percentage completion calculators.
- **Acceptance Criteria:** Managers and employees create and track quarterly goals; cycle deadlines trigger automated notifications.

---

### Milestone 15: 360-Degree Feedback Synthesis & AI-Assisted Review Drafting
- **Objective:** Facilitate peer, self, and manager reviews, synthesizing diverse multi-perspective feedback into balanced, objective AI-assisted summaries.
- **Key Deliverables:**
  - Endpoints: `POST /api/v1/performance/reviews/submit`, `POST /api/v1/performance/reviews/{id}/ai-summarize`.
  - LLM synthesis prompt reducing bias, balancing constructive feedback, and highlighting achievements.
  - Manager review approval and sign-off workflow.
- **Technical Specs:** LLM Router with prompt engineered for anti-bias calibration and managerial tone.
- **Acceptance Criteria:** 360-feedback inputs are securely consolidated; AI synthesis generates accurate, non-toxic, actionable review summaries.

---

### Milestone 16: React/Vite Frontend Self-Service Portal & HR Admin Dashboard
- **Objective:** Build a responsive, accessible React/TypeScript single-page application for employee self-service and HR administration.
- **Key Deliverables:**
  - Employee Self-Service: Dashboard, Onboarding Checklist, Leave Balances & Request Modal, Policy AI Chat Assistant.
  - HR Admin Portal: Employee Directory, Leave Approvals Table, Policy Uploader & Acknowledgment Matrix, Review Cycle Manager.
  - TanStack Query data caching, role-gated routes, Tailwind CSS theme.
- **Technical Specs:** Vite, React 18, TypeScript, Tailwind CSS, Lucide icons, TanStack Query.
- **Acceptance Criteria:** Frontend renders responsive UI across desktop and mobile, with role-based UI component visibility.

---

### Milestone 17: End-to-End Integration Testing, Security Audits & Production Deployment
- **Objective:** Perform end-to-end integration tests, security pentesting, OpenAPI documentation validation, and production CI/CD deployment configuration.
- **Key Deliverables:**
  - Pytest async integration suite covering the entire lifecycle (recruiter webhook -> onboarding -> leave -> policy RAG -> performance review).
  - GitHub Actions CI/CD workflows (linting, test coverage, Docker image packaging).
  - Production Helm chart / Docker Compose production override with zero-leak secret configs.
- **Technical Specs:** Pytest, HTTPX test client, GitHub Actions, Docker multi-stage builds.
- **Acceptance Criteria:** Test suite passes with >85% code coverage; zero critical security vulnerabilities identified; automated CI/CD builds deploy successfully.
