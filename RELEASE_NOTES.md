# Release v2.1.0 — `ai-hr-platform` (Production Hardening & Enterprise Expansion)

**Release Date:** November 26, 2026  
**License:** Apache 2.0  
**Status:** Production Ready  

Version 2.1.0 unites end-to-end production hardening across database migrations, Redis-backed authentication & rate limiting, and Prometheus observability with major enterprise capabilities: Federated SSO (SAML 2.0 / OIDC) + RFC 6238 TOTP MFA, an Event-Driven Notification & Digest Engine, and AI Workforce Planning with `ai-recruiter` sync.

---

## 🔒 Production Hardening (Track A)

- **Complete Enterprise Alembic Schema (`0002_v2_1_enterprise_schema.py`)**: Aligned foreign-key UUID column types across 13 domain models and added full migration coverage for all v1.1–v2.1 tables (`alembic upgrade head` verified in CI).
- **Redis-Backed Auth Revocation, Logout & Refresh Rotation**: Upgraded `revoke_token_jti` / `is_jti_revoked` to Redis with TTL + thread-safe in-memory fallback, added `POST /api/v1/auth/logout`, and enforced refresh token rotation in `POST /api/v1/auth/refresh`.
- **Redis Scoped Rate Limiting**: Added sliding/fixed-window Redis rate limiter (`rate_limit`) protecting `/auth/login` and `/policies/chat` with standard `X-RateLimit-*` and `Retry-After` headers.
- **Prometheus & Kubernetes Probes**: Replaced in-memory `/metrics` with `prometheus-client` exposition (`ai_hr_http_requests_total`, `ai_hr_http_request_duration_seconds`, `ai_hr_http_requests_in_flight`), added `/health/live` & `/health/ready` (checking PostgreSQL + Redis), and added structured JSON logging with `X-Request-ID` correlation IDs.
- **Grouped Sidebar Navigation & Code Splitting**: Added History API URL routing (`useRoute`), a searchable collapsible left sidebar, and `React.lazy` route-level Vite chunk splitting.

## 🚀 New Enterprise Features (Track B)

- **Enterprise SSO (SAML 2.0 / OIDC) & TOTP MFA (`/api/v1/security`, `SecuritySsoMfaView`)**: PKCE `S256` OIDC handshakes, XXE-hardened SAML 2.0 XML response parsing via `defusedxml`, and RFC 6238 TOTP provisioning with hashed backup recovery codes.
- **Event-Driven Notification & Digest Engine (`/api/v1/notifications`, `NotificationsCenterView`)**: Multi-channel inbox (`EMAIL`, `SLACK`, `TEAMS`, `IN_APP`) with Celery Beat scheduled daily HR digests and visa/compliance expiration scans.
- **AI Workforce Planning & Headcount Forecasting (`/api/v1/workforce-planning`, `WorkforcePlanningView`)**: Departmental headcount modeling (1.28x fully-loaded cost multiplier), Conservative/Baseline/Hypergrowth scenario simulation, and HMAC-SHA256 signed `ai-recruiter` requisition syncing.
- **Python & TypeScript SDK Parity (`v2.1.0`)**: Updated `packages/ai-hr-sdk-python`, `packages/ai-hr-sdk-ts`, and `docs/api_collection.json`.

---

# Release v2.0.1 — `ai-hr-platform` (Security & Quality Patch)

**Release Date:** November 22, 2026  
**License:** Apache 2.0  
**Status:** Production Ready  

Version 2.0.1 delivers comprehensive security hardening, zero-vulnerability dependency remediation, and architectural import bug fixes across the platform.

---

## 🛡️ Security Hardening & Bug Fixes in v2.0.1

### 1. High-Severity Dependency Remediation (Vite 6.4.6)
- Remediated high-severity CVE vulnerability in `vite <=6.4.3` (`GHSA-4w7w-66w2-5vf9` and Windows path traversal advisories).
- Upgraded and pinned `vite@^6.4.6` in `package.json` and package overrides.
- Achieved **0 vulnerabilities** across all 140 frontend packages in `npm audit`.

### 2. Missing Endpoint Dependency & Alias Fix (`backend.app.api.v1.deps`)
- Resolved runtime import issue where 8 microservice modules (`attendance`, `benefits`, `coaching`, `compliance`, `offboarding`, `outbound_webhooks`, `pulse`, `succession`) imported from `backend.app.api.v1.deps`.
- Implemented `backend/app/api/v1/deps.py` and exported `get_db`, `get_current_user`, `require_role`, and backwards-compatible alias `require_roles`.

### 3. Active JWT Revocation & Anti-Replay Guard
- Implemented in-memory JTI revocation registry (`REVOKED_JTIS`, `revoke_token_jti`, `is_jti_revoked`) in `security.py`.
- Enforced strict token claim verification (`verify_exp`, `verify_nbf`, `verify_iat`) and immediate rejection of revoked tokens in authentication dependencies.

### 4. Production Secret Key Guardrail
- Added Pydantic field validation in `Settings` preventing accidental deployments in `ENVIRONMENT=production` with default placeholder `SECRET_KEY`.

### 5. Enhanced LLM Prompt Injection & Delimiter Neutralization
- Expanded prompt injection tokenizer patterns in `llm_router.py` to neutralize `<|system|>`, `<|user|>`, `[SYS]`, and `human:` / `assistant:` delimiters.
- Broadened adversarial jailbreak detection in `policy_rag_service.py` to intercept system instruction overrides, database dump attempts, and environment variable exfiltration queries.

---

# Release v2.0.0 — `ai-hr-platform` (Major Milestone)

**Release Date:** November 22, 2026  
**License:** Apache 2.0  
**Status:** Production Ready  

Version 2.0.0 marks a major architectural milestone for `ai-hr-platform`, delivering market salary intelligence with compa-ratio retention audits, an end-to-end global visa and immigration case management engine with tax-grossed relocation disbursements, and a multi-tenant white-label branding suite with custom CNAME domain routing and cryptographic KMS key isolation.

---

## 🌟 What's New in v2.0.0

### 1. AI Compensation Benchmarking & Market Salary Intelligence
- **Radford & Option Impact Market Percentiles (`/api/v1/benchmarking`):**
  - Continuous market compensation intelligence curves across `P25`, `P50` (median), `P75`, and `P90` percentiles for base pay, equity shares, and variable bonuses.
- **Geographic Cost-of-Labor Multipliers:**
  - Dynamic adjustments across geographic talent zones (Bay Area 1.25x, NYC 1.20x, Tier-2 Tech Hubs 1.05x, Remote US 1.00x, London, Berlin, Tokyo).
- **Automated Compa-Ratio Parity & Retention Risk Audits (`GET /api/v1/benchmarking/audit/department`):**
  - Computes employee compa-ratios (`current_base / market_p50`), categorizes band positions (`BELOW_RANGE`, `LOWER_QUARTILE`, `AT_MARKET`, `UPPER_QUARTILE`), flags flight risks, and forecasts departmental budget gaps to median.
- **Salary Benchmarking Portal (`SalaryBenchmarkingView.tsx`):**
  - Departmental compa-ratio dashboards, suggested merit adjustment recommendations, and market percentile curves.

### 2. Visa, Global Immigration & Relocation Management
- **End-to-End Legal Petition Tracking (`/api/v1/immigration/cases`):**
  - Manages petitions across H-1B, L-1A/B, O-1, TN, and PERM Permanent Residency with automated case status progression (`INTAKE`, `DOL_PREVAILING_WAGE`, `USCIS_SUBMITTED`, `APPROVED`).
- **USCIS Integration & Expiration Watchlist:**
  - Receipt number tracking (e.g. `WAC-26-901-XXXXX`), adjudication center assignment, and automated alerts for petitions expiring within 90 days.
- **Tax Gross-Up Relocation Disbursements (`POST /api/v1/immigration/cases/{id}/disburse-stipend`):**
  - Automated 32% supplemental tax gross-up calculation guaranteeing employees receive full net relocation stipends via direct payroll ACH.
- **Immigration Portal (`ImmigrationRelocationView.tsx`):**
  - Petition timeline tracker, document verification counters, and relocation payout triggers.

### 3. Multi-Tenant Enterprise White-Labeling & Custom Domain Routing
- **Custom CNAME Domain Ingress (`/api/v1/branding`):**
  - Organizations can route branded portals through custom corporate domains (e.g. `people.acme.corp`) with automated DNS CNAME resolution and TLS/SSL certificate issuance.
- **Visual Brand Palette & Theme Engine:**
  - Per-tenant customizable primary and secondary brand colors, custom vector logos, portal titles, and dedicated support emails.
- **KMS Tenant Data Isolation:**
  - Dedicated Customer Managed Key (CMK) encryption keys per tenant ensuring complete cryptographic isolation.
- **White-Label Portal (`TenantBrandingView.tsx`):**
  - Configuration console with interactive live preview widget demonstrating branded headers and secure portals.

---

# Release v1.9.0 — `ai-hr-platform`

**Release Date:** November 22, 2026  
**License:** Apache 2.0  
**Status:** Production Ready  

Version 1.9.0 expands the platform with an enterprise Learning & Development (L&D) / Mandatory Compliance LMS with verifiable digital certificates, an IT Hardware & Asset Fleet Management system with MDM integration and zero-touch remote wipe, and a Global Contractor & Vendor Employer of Record (EOR) Hub with automated W-8BEN/W-9 audit verification and cross-border milestone payouts.

---

## 🌟 What's New in v1.9.0

### 1. Learning & Development (L&D) & Mandatory Compliance LMS
- **Statutory & Role-Based Course Catalog (`/api/v1/learning`):**
  - Pre-seeded modules: Annual SOC 2 Information Security Awareness, Preventing Workplace Harassment (CA/NY standard), HIPAA Privacy & Security, and Cloud Native Architecture.
- **Progress Tracking & Digital Certificates:**
  - Automated progress tracking, exam scoring against passing thresholds, and generation of verifiable certificate IDs (`CERT-YYYY-XXXX`).
  - Automated certificate expiration tracking and recertification cycle calculations.
- **Enterprise Compliance Audit (`GET /api/v1/learning/compliance-audit`):**
  - Aggregates company-wide compliance completion rates, identifies overdue recertifications, and provides automated auditor recommendations.
- **Interactive LMS Dashboard (`LearningDevelopmentView.tsx`):**
  - Category filters, progress sliders, instant exam completion, and digital credential verification cards.

### 2. Enterprise Hardware & Asset Fleet Management
- **Hardware Inventory Lifecycle (`/api/v1/assets`):**
  - Register workstations, monitors, and security keys with serial numbers, asset tags, purchase dates, warranty expirations, and device condition grades.
- **MDM Provider Integration & Device Health:**
  - Support for Jamf Pro, Microsoft Intune, and Kandji MDM profiles with automated check-in logging.
- **Cryptographic Remote Wipe Protocol (`POST /api/v1/assets/{id}/remote-wipe`):**
  - Dispatch zero-touch sanitization commands across enrolled devices during offboarding or critical security breach protocols.
- **Asset Directory & Fleet Portal (`AssetFleetView.tsx`):**
  - Asset status indicators, one-click assign/return actions, fleet metrics, and remote wipe confirmation modal.

### 3. Global Contractor & Vendor EOR (Employer of Record) Hub
- **International Contractor Registry (`/api/v1/contractors`):**
  - Multi-country contractor onboarding supporting individuals, LLCs, and corporations with hourly rate and currency configuration.
- **Tax Compliance & Audit Verification:**
  - W-8BEN (foreign individuals), W-8BEN-E (foreign entities), W-9, and VAT registration collection and one-click verification audits.
- **Statements of Work (SOWs) & Milestone Invoices:**
  - Milestone-based deliverables tracking against fixed budgets.
  - Manager approval workflow and automated cross-border payout disbursement generating traceable payment hashes (`TX-EOR-{CURRENCY}-{HASH}`).
- **Global EOR Hub View (`ContractorEorView.tsx`):**
  - Contractor roster, tax compliance status badges, milestone invoice ledger, and international wire execution buttons.

---

# Release v1.8.0 — `ai-hr-platform`

**Release Date:** November 22, 2026  
**License:** Apache 2.0  
**Status:** Production Ready  

Version 1.8.0 introduces an AI-powered expense reimbursement engine with automated receipt policy auditing, an enterprise workplace health and safety incident tracker with OSHA 300 / 300A compliance logs and AI root-cause analysis, and an employee rewards, peer kudos, and milestone celebration engine.

---

## 🌟 What's New in v1.8.0

### 1. AI Expense Reimbursement & OCR Policy Auditor
- **Multi-Category Expense Reporting (`/api/v1/expenses`):**
  - Itemized submission across `MEALS`, `TRAVEL`, `LODGING`, `SOFTWARE`, `OFFICE_SUPPLIES`, and `OTHER`.
- **Autonomous Policy Compliance Auditor (`POST /api/v1/expenses/{id}/audit`):**
  - Flags per-diem violations (e.g. meal expenses > $75.00 limit, lodging > $300.00).
  - Enforces mandatory itemized receipt attachments for any item exceeding $25.00.
  - Automatically flags alcohol-related purchases for corporate entertainment policy compliance.
  - Identifies non-working weekend expense dates requiring pre-authorization justifications.
- **Automated Reimbursement Payouts:**
  - One-click manager approval workflow generating traceable ACH reimbursement reference codes (e.g. `REIMB-YYYYMMDD-XXXXXX`).
- **Interactive Expense Portal (`ExpenseAuditView.tsx`):**
  - Visual policy inspection breakdown, total outlay metrics, compliance pass rate KPI, and new expense report filing modal.

### 2. Workplace Health, Safety & OSHA Incident Compliance Tracker
- **OSHA 29 CFR Part 1904 Compliance Engine (`/api/v1/safety`):**
  - Automatic evaluation of OSHA recordability based on medical treatment beyond first aid, restricted duty, or days away from work.
  - Automatic generation of sequential OSHA case numbers (e.g. `OSHA-2026-XXXX`).
- **Automated OSHA Form 300 / 300A Log Computation:**
  - Aggregates annual injury, illness, and near-miss case counts.
  - Computes standard Lost Workday Rate (LWDR) per 200,000 labor hours (100 FTE baseline).
- **AI 5-Whys Root Cause Analysis & Mitigation Plans:**
  - Synthesizes incident narratives and locations into environmental/procedural root causes with targeted engineering controls.
- **Safety Incident Portal (`SafetyComplianceView.tsx`):**
  - Live incident register, OSHA recordable badges, and deep root-cause inspection modal.

### 3. Employee Rewards, Peer Kudos & Milestone Celebration Engine
- **Peer Recognition & Micro-Bonus Feed (`/api/v1/recognition/feed`):**
  - Colleague recognition feed tied directly to corporate core values (`CUSTOMER_OBSESSION`, `BIAS_FOR_ACTION`, `INNOVATION_EXCELLENCE`, `DELIVER_RESULTS`, `OWNERSHIP`).
- **Discretionary Point Wallets & Allowance Management:**
  - Monthly giving allowance (default 200 pts/month) prevents point inflation; redeemable point wallets for received peer appreciation.
- **Rewards Catalog & Instant Claim Redemption (`/api/v1/recognition/rewards`):**
  - Built-in reward tiers (digital gift cards, noise-cancelling headphones, branded company fleece kits, and extra paid wellness days off).
  - Validation of point balance and generation of unique redemption claim codes (`RWD-XXXXXXXX`).
- **Automated Milestone Detection:**
  - Tracking and celebration feed for employee work anniversaries and birthdays with automated bonus point allocations.
- **Recognition Portal (`RewardsRecognitionView.tsx`):**
  - Interactive kudos composer, real-time activity stream, and instant catalog redemption shop.

---

# Release v1.7.0 — `ai-hr-platform`

**Release Date:** November 22, 2026  
**License:** Apache 2.0  
**Status:** Production Ready  

Version 1.7.0 delivers autonomous employee sentiment and burnout radar tracking with cryptographic zero-identifiability, an automated benefits administration engine with an AI open-enrollment advisor, and a statutory FLSA time and attendance compliance engine.

---

## 🌟 What's New in v1.7.0

### 1. Autonomous Employee Pulse & Team Sentiment Radar
- **Anonymous Micro-Pulse Engine (`/api/v1/pulse`):**
  - Instant and recurring employee pulse surveying with Likert scores across work-life balance, psychological safety, leadership alignment, and role clarity.
- **Zero-Identifiability Cryptographic Privacy:**
  - Respondent identity protected by SHA-256 salted hash decoupling (`user_id + survey_id + salt`), enforcing one-response-per-employee integrity without ever persisting raw employee identifiers on survey response records.
- **eNPS & Burnout Watchlist Analytics:**
  - Automated calculation of Employee Net Promoter Score (eNPS) from promoter/passive/detractor distributions.
  - Multi-dimensional burnout index calculation with threshold-triggered department alert status (`HEALTHY`, `MODERATE`, `BURNOUT_RISK`).
- **AI Action Recommendations:**
  - Autonomous synthesis of low-scoring sentiment facets into targeted manager and HR leadership interventions.
- **Interactive Sentiment Radar (`PulseSentimentView.tsx`):**
  - Real-time departmental metrics, eNPS indicator badges, and direct response capture modal.

### 2. Automated Benefits Administration & AI Open Enrollment Advisor
- **Comprehensive Benefit Catalog (`/api/v1/benefits`):**
  - Pre-seeded enterprise healthcare and wellness tiers: Standard PPO, High-Deductible Health Plan (HDHP + HSA), Comprehensive Dental, and Vision Care.
- **Tier-Based Payroll Deductions:**
  - Automated employer/employee premium split calculation supporting `EMPLOYEE_ONLY`, `EMPLOYEE_SPOUSE`, `EMPLOYEE_CHILDREN`, and `FAMILY` coverage tiers.
- **AI Autonomous Benefits Advisor (`POST /api/v1/benefits/advisor`):**
  - Context-grounded advisory engine evaluating employee family size, anticipated medical visits, and prescription needs to recommend optimal health plans and HSA savings strategies.
- **Self-Service Enrollment Portal (`BenefitsEnrollmentView.tsx`):**
  - Plan comparison matrix, interactive election selector, and AI plan advisory assistant.

### 3. Time & Attendance Engine with Statutory FLSA Overtime Compliance
- **Time Clock & Timesheet Management (`/api/v1/attendance`):**
  - Employee punch-in, punch-out, and break logging with automated shift duration calculation.
- **Statutory Overtime Compliance Rules Engine:**
  - Automated FLSA and state labor standard compliance computation:
    - Regular hours: <= 8.0 hours/day.
    - 1.5x Overtime: > 8.0 and <= 12.0 hours/day.
    - 2.0x Double-Time: > 12.0 hours/day.
- **Meal Break Penalty Violation Auditing:**
  - Proactive audit flag triggered for shifts exceeding 6.0 hours with under 30 minutes of meal break time.
- **Time & Attendance Portal (`TimeAttendanceView.tsx`):**
  - Real-time punch clock interface, historical timesheet records table, and compliance audit status indicators.

---

# Release v1.6.0 — `ai-hr-platform`

**Release Date:** November 22, 2026  
**License:** Apache 2.0  
**Status:** Production Ready  

Version 1.6.0 expands the platform with an automated employee offboarding & de-provisioning engine, an interactive visual organization chart & span-of-control analytics suite, and an AI-driven 1:1 coaching & performance calibration assistant.

---

## 🌟 What's New in v1.6.0

### 1. Automated Employee Offboarding & Asset Reclamation Lifecycle
- **End-to-End Offboarding Protocol (`/api/v1/offboarding`):**
  - Manages departure checklists across IT, Finance, HR, and Security domains.
  - Generates automated shipping return tasks for laptops and hardware with wipe certification tracking.
  - Final paystub and accrued PTO payout tracking.
- **SCIM 2.0 Automated Deprovisioning (`POST /api/v1/offboarding/{id}/deprovision-scim`):**
  - Instant one-click or scheduled account suspension across corporate IdPs (Okta, Microsoft Entra ID, Google Workspace, GitHub Enterprise).
- **Exit Interview AI Synthesis:**
  - Automated sentiment scoring and retention root-cause analysis (e.g. compensation, career trajectory, manager relationship).
- **Offboarding Dashboard (`OffboardingView.tsx`):**
  - Web view for people managers and HR administrators to monitor departure workflows and task completion.

### 2. Interactive Enterprise Org Chart & Hierarchy Analytics
- **Visual Reporting Tree (`OrgChartView.tsx`):**
  - Canvas-style recursive hierarchy visualizer rendering executive nodes down to individual contributors with drill-down collapse/expand controls.
- **Span-of-Control Analytics (`GET /api/v1/employees/org-chart/stats`):**
  - Real-time computation of average direct reports per manager and overloaded manager alerts (>8 direct reports threshold).

### 3. AI Autonomous 1:1 Coaching & Performance Calibration
- **1:1 Coaching Co-Pilot (`/api/v1/coaching/1on1`):**
  - Generates meeting agendas dynamically grounded in the direct report's active OKRs, recent project milestones, and blockers.
  - Generates tailored coaching prompts for managers based on strategic focus areas (`CAREER_GROWTH`, `PERFORMANCE_INTERVENTION`, `GENERAL_PROGRESS`).
- **Performance Calibration & Bias Detector (`/api/v1/coaching/calibration`):**
  - Statistical analysis of departmental rating distributions.
  - Automatically identifies and flags **Central Tendency Bias** (clustering at rating 3), **Leniency Bias** (skewed upper distribution), and **Harshness Bias** (skewed lower distribution).
- **Coaching & Calibration Dashboard (`CoachingCalibrationView.tsx`):**
  - Dual-mode interface supporting manager check-in agendas and executive calibration audits.

---

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
