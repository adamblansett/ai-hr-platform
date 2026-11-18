# Release v1.5.0 — `ai-hr-platform`

**Release Date:** November 18, 2026  
**License:** Apache 2.0  
**Status:** Production Ready  

Version 1.5.0 introduces comprehensive enterprise security hardening: dependency vulnerability remediation (npm audit / esbuild & picomatch overrides), unprivileged non-root container isolation for backend and frontend, Nginx reverse proxy rate-limiting and buffer overflow defenses, HTTP security headers middleware (HSTS, CSP, X-Frame-Options DENY), JWT replay mitigation with unique `jti` and `nbf` claims, and prompt injection / adversarial jailbreak defense guardrails for LLM RAG queries.

---

## 🌟 What's New in v1.5.0

### 1. Application & Container Hardening
- **Unprivileged Non-Root Execution:**
  - `backend/Dockerfile`: Created isolated `appuser` (UID 10001) with unprivileged system permissions; dropped root execution.
  - `frontend/Dockerfile`: Migrated to `nginxinc/nginx-unprivileged:alpine` running non-root on port 8080.
- **Frontend Dependency Vulnerability Remediation:**
  - Pruned unused `react-router-dom` to eliminate CVE-2025-68470 open-redirect risk.
  - Configured npm overrides for secure `esbuild` and `picomatch` releases.

### 2. Network & Gateway Defense (Nginx & Middleware)
- **Nginx Security Hardening (`docker/nginx/nginx.conf`):**
  - Suppressed server version disclosure (`server_tokens off;`).
  - Added buffer overflow protections (`client_body_buffer_size 128k`, `client_max_body_size 25M`, `large_client_header_buffers 4 8k`).
  - Implemented dual rate-limiting zones: `auth_limit` (5 req/s with burst of 10 for credential endpoints) and `api_limit` (30 req/s with burst of 20 for general API routes).
- **FastAPI HTTP Security Headers:**
  - Injected strict HTTP headers: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`, and `Content-Security-Policy` with iframe denial.

### 3. Authentication & Adversarial LLM Guardrails
- **JWT Anti-Replay Protection (`backend/app/core/security.py`):**
  - Added unique `jti` (JWT ID via 128-bit UUID) and `nbf` (not before timestamp) claims to all access and refresh tokens.
- **Adversarial Prompt Injection Guardrail (`backend/app/services/policy_rag_service.py`):**
  - Real-time heuristic detection filtering adversarial system prompt override attempts (`ignore previous instructions`, `you are now DAN`, etc.) before forwarding queries to the LLM.

---

# Release v1.4.0 — `ai-hr-platform`

**Release Date:** November 18, 2026  
**License:** Apache 2.0  
**Status:** Production Ready  

Version 1.4.0 delivers the complete ecosystem developer and operational package: an interactive 8-stage terminal demo tour script, an Outbound Integrations and Webhooks frontend management view, automated CI security and SAST scanning (Bandit, Trivy, Gitleaks), and official client SDKs for both Python and TypeScript.

---

## 🌟 What's New in v1.4.0

### 1. Interactive End-to-End Enterprise Tour CLI (`backend/scripts/demo_tour.py`)
- Standalone executable script demonstrating all 8 critical lifecycle milestones in sequence:
  1. Recruiter handoff offer acceptance webhook with HMAC-SHA256 signature verification.
  2. Role-specific 5-point onboarding checklist generation.
  3. Form I-9 document OCR with digital signature detection.
  4. Multilingual Policy RAG handbook query with zero-leak PII scrubbing.
  5. Departmental calendar overlap and PTO conflict detection.
  6. Gross-to-net payroll deductions and 48-month equity vesting with a 1-year cliff.
  7. Outbound webhook event signing for downstream HRIS (Workday/ADP).
  8. GDPR Article 15 DSAR bundle packaging with SHA-256 seal integrity verification.

### 2. Outbound Webhooks & HRIS Integrations Dashboard (`IntegrationsView.tsx`)
- Web management portal for administrators to register, manage, and monitor outbound webhooks.
- Multi-event trigger selection (`employee.hired`, `leave.approved`, `equity.vested`, `compensation.updated`).
- Real-time **Test Ping** button providing instant simulation with `X-AI-HR-Signature-256` HMAC previews.

### 3. Automated Security Scanning & DevSecOps CI Pipeline (`.github/workflows/security.yml`)
- **Bandit SAST Linter:** Scans Python backend codebase for security anti-patterns.
- **Trivy Container & Repo Scanner:** Scans containers and dependencies for CVEs.
- **Gitleaks:** Continuous secret detection across all commits and PRs.

### 4. Official Python & TypeScript Client SDKs
- **Python SDK (`packages/ai-hr-sdk-python/`):** Full client library with authentication, policy RAG querying, compensation metrics, and outbound webhook dispatch.
- **TypeScript SDK (`packages/ai-hr-sdk-ts/`):** Typed client package with full interfaces for Node.js and frontend consumers.

---

# Release v1.3.0 — `ai-hr-platform`

**Release Date:** November 18, 2026  
**License:** Apache 2.0  
**Status:** Production Ready  

Version 1.3.0 delivers multi-cloud Infrastructure as Code (Terraform for AWS & GCP), automated test suites covering compensation, flight risk, and compliance verification, Playwright E2E browser flows for the Enterprise Suite, and an event-driven outbound webhook subscription engine for downstream HRIS/ERP integrations (Workday, ADP, Gusto).

---

## 🌟 What's New in v1.3.0

### 1. Multi-Cloud Infrastructure as Code (Terraform / OpenTofu)
- **AWS Production Architecture (`deploy/terraform/aws/`):**
  - **VPC & Subnets:** Isolated multi-AZ private subnets for stateful workloads.
  - **RDS Aurora PostgreSQL 16:** Cluster with native `pgvector` shared library preloading and automated multi-AZ failover.
  - **ElastiCache Redis 7:** Dedicated Redis instance for rate limiting and Celery worker queuing.
  - **S3 Document Vault:** Server-side encrypted storage with AWS KMS customer-managed key rotation.
- **Google Cloud Platform Architecture (`deploy/terraform/gcp/`):**
  - **Cloud SQL PostgreSQL 16:** Managed instance with `cloudsql.enable_pgvector=on`.
  - **GKE Autopilot:** Production Kubernetes cluster auto-scaling with workload identity.
  - **Cloud Storage Vault:** KMS-encrypted bucket with uniform bucket-level access control.

### 2. Event-Driven Outbound Webhook Subscriptions (`/api/v1/webhooks/outbound`)
- **Third-Party Integration Hub:**
  - Enables downstream payroll providers (ADP, Gusto, Workday) and IT systems to subscribe to real-time events (`employee.hired`, `leave.approved`, `equity.vested`, `compensation.updated`).
  - Cryptographic HMAC-SHA256 signature generation (`X-AI-HR-Signature-256`) per subscription secret.
  - Delivery logs and simulated test-ping endpoint (`POST /api/v1/webhooks/outbound/subscriptions/{id}/test-ping`).

### 3. Comprehensive Automated Verification Suite
- **Unit & Integration Tests (`backend/tests/`):**
  - `test_compensation.py`: Validates 1-year cliff equity vesting and federal/FICA/medicare tax calculations.
  - `test_succession.py`: Validates candidate skill overlap percentages and flight-risk categorization thresholds.
  - `test_compliance.py`: Validates SHA-256 integrity seal tampering detection and GDPR Article 17 PII redaction.
- **Playwright E2E Test Suite (`frontend/tests/e2e/enterprise.spec.ts`):**
  - Automated browser tests verifying end-to-end user navigation through Compensation & Equity, Global Statutory Holidays, and SOC 2 / GDPR Compliance dashboards.

---

# Release v1.2.0 — `ai-hr-platform`

**Release Date:** November 18, 2026  
**License:** Apache 2.0  
**Status:** Production Ready  

Version 1.2.0 completes the comprehensive Enterprise Suite: frontend interactive views for compensation/equity, international holidays, and multilingual policy RAG; AI-driven succession planning with flight-risk prediction and requisition skill matching; and an enterprise compliance vault featuring GDPR/CCPA Data Subject Access Request (DSAR) packaging, Article 17 Right to Erasure, and real-time SOC 2 Type II audit readiness reporting.

---

## 🌟 What's New in v1.2.0

### 1. Enterprise UI Expansion (React 18 / TypeScript / Tailwind CSS)
- **Compensation & Equity Dashboard (`CompensationView.tsx`):**
  - Self-service annual base salary, target bonus, and total compensation breakdown.
  - Interactive equity grant viewer with 48-month linear vesting progression and 1-year cliff threshold indicators.
  - Historical paystub table with federal, FICA, medicare, and state tax deductions.
- **Global & Holiday Calendar View (`LocalizationView.tsx`):**
  - Regional statutory holiday calendar toggle for United States, United Kingdom, Germany, and Japan.
  - Interactive multilingual policy assistant tester supporting Spanish, French, German, and Japanese.
- **Compliance & Governance Dashboard (`ComplianceView.tsx`):**
  - Live SOC 2 Type II control monitor (CC6.1 Access Control, CC6.6 Data Protection, CC7.2 Audit Integrity, CC2.1 Policy Governance).
  - AI Flight-Risk calibration view for people managers and HR executives.
  - One-click GDPR Data Subject Access Request (DSAR) generator with SHA-256 seal verification.

### 2. AI-Driven Succession Planning & Career Mobility
- **Skill Competency Taxonomy (`/api/v1/succession/skills`):**
  - Structured employee skill tracking across technical, leadership, domain, and compliance categories.
- **Predictive Retention & Flight-Risk Engine (`/api/v1/succession/flight-risk`):**
  - Calculates retention flight risk (0.0 to 1.0) and assigns risk tiers (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) using role tenure, market compensation ratio, and performance reviews.
  - Generates recommended interventions (e.g. spot compensation reviews, promotion evaluations, lateral stretch projects).
- **Internal Mobility Candidate Matcher (`/api/v1/succession/requisitions/{id}/match`):**
  - Matches active employees against open requisitions by computing skill overlap and identifying skill gaps for targeted upskilling.

### 3. Enterprise Compliance & Data Governance Vault
- **GDPR / CCPA DSAR Bundle Exporter (`GET /api/v1/compliance/dsar/{id}`):**
  - Compiles full subject dossier (profile, onboarding tasks, document OCR logs, leave requests, compensation, paystubs, policy digital signatures) into a structured JSON export protected with a cryptographic SHA-256 integrity seal.
- **GDPR Article 17 Right-to-be-Forgotten Engine (`POST /api/v1/compliance/right-to-be-forgotten/{id}`):**
  - Safely anonymizes personal identity records (name, email, phone) to pseudonymous tokens while preserving tamper-evident audit history.
- **SOC 2 Type II Evidence Summary (`GET /api/v1/compliance/soc2/evidence`):**
  - Aggregates automated audit evidence covering RBAC identities, Zero-Leak PII scrubbing, immutable audit trails, and cryptographic policy signatures.

---

# Release v1.1.0 — `ai-hr-platform`

**Release Date:** November 18, 2026  
**License:** Apache 2.0  
**Status:** Production Ready  

Version 1.1.0 introduces full-cycle payroll calculation, equity compensation with vesting schedule simulation, multilingual RAG localized across 7 languages, global statutory holiday calendars (US, UK, DE, JP), and an end-to-end multi-service ecosystem orchestrator connecting `ai-recruiter` and `ai-hr-platform`.

---

## 🌟 What's New in v1.1.0

### 1. Payroll & Equity Compensation Engine
- **Salary & Compensation Packages (`/api/v1/compensation`):**
  - Manages base salary, payment frequency (`MONTHLY`, `BIWEEKLY`, `SEMIMONTHLY`), target bonus %, and currency code.
  - Automated payroll calculation with tax withholding estimations: Federal Income Tax (22%), Social Security (6.2%), Medicare (1.45%), and State Tax (5%).
  - Detailed paystub generation with gross-to-net breakdown and unique paystub tracking numbers.
- **Equity Grants & Cliff/Vesting Schedules:**
  - Support for ISO, NSO, and RSU equity grant types.
  - Built-in vesting schedule simulator with standard 1-year cliff and 48-month linear vesting progression.
  - Employee self-service `/api/v1/compensation/me` reporting vested vs. unvested shares, current estimated valuation, and next vesting date.

### 2. Multilingual Policy RAG & Statutory Holiday Localization
- **Multilingual Knowledge Engine (`/api/v1/localization`):**
  - Zero-latency heuristic language detector supporting English (`en`), Spanish (`es`), French (`fr`), German (`de`), Japanese (`ja`), Portuguese (`pt`), and Chinese (`zh`).
  - Native language prompt augmentation for RAG responses, allowing international employees to query company handbooks in their mother tongue while citing exact clause sources.
- **Global Statutory Public Holiday Calendar:**
  - Pre-seeded statutory holiday calendars across four major enterprise jurisdictions: United States (`US`), United Kingdom (`UK`), Germany (`DE`), and Japan (`JP`).
  - Seamless integration with the leave management engine to prevent PTO deductions on recognized legal holidays.

### 3. Ecosystem Orchestration (`docker/ecosystem-compose.yml`)
- **Multi-Service Interconnect:**
  - Dedicated Docker Compose definition bridging `ai-recruiter` (upstream hiring workflow) and `ai-hr-platform` (onboarding and employee lifecycle) across a unified network bridge (`recruiter_hr_bridge`).
- **Automated End-to-End Orchestrator (`backend/scripts/ecosystem_e2e_runner.py`):**
  - Automated runner executing the full hiring-to-onboarding lifecycle: candidate offer acceptance, cryptographic HMAC webhook delivery, employee profile provisioning, task checklist generation, and welcome package dispatch.

---

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
