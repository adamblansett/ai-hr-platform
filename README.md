# ai-hr-platform

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

`ai-hr-platform` is an independently deployable open-source microservice engineered to automate enterprise employee lifecycle operations, compliance tracking, leave management, and AI-assisted employee support.

It seamlessly integrates downstream with [`ai-recruiter`](https://github.com/example/ai-recruiter) upon candidate offer acceptance, provisioning employee onboarding workflows and serving as the intelligent system of record for employee operations.

---

## Key Features

1. **Employee Lifecycle & Onboarding:**
   - Automated onboarding task checklist orchestration.
   - Cryptographically signed HMAC-SHA256 webhook handoff from `ai-recruiter` upon offer acceptance.
   - Compliance documentation collection and digital acknowledgment tracking.

2. **Centralized Directory & Self-Service:**
   - Multi-tenant data isolation and Role-Based Access Control (`SUPER_ADMIN`, `HR_ADMIN`, `PEOPLE_MANAGER`, `EMPLOYEE`).
   - Reporting hierarchy / organizational chart navigation.
   - Self-service portal for personal information updates and inquiries.

3. **Policy Enforcement & RAG Knowledge Base:**
   - Automated ingestion of employee handbooks, labor regulations, and SOPs.
   - Semantic vector indexing powered by PostgreSQL `pgvector`.
   - Context-grounded Q&A assistant providing direct citations to policy clauses.

4. **Leave & Attendance Tracking:**
   - Multi-tier accrual engine (PTO, Sick, Parental, Bereavement) with rollover caps.
   - Managerial approval workflows with concurrent team calendar conflict detection.
   - Scheduled balance auditing and adjustments.

5. **Performance Management & OKRs:**
   - Structured performance cycles and goal/OKR progress tracking.
   - 360-degree feedback collection (self, manager, peer, direct report).
   - AI-assisted feedback summarization with built-in anti-bias guardrails.

6. **Privacy & Security First:**
   - Pre-inference regex and pattern-based PII scrubber (SSN, credit card, phone, personal email).
   - Provider-agnostic inference layer supporting local models via Ollama (`Llama 3.1 8B`, `Qwen 2.5 7B`, `Mistral NeMo 12B`) alongside cloud fallbacks.
   - Immutable audit logging for all compliance-relevant entity mutations.

---

## Technical Stack

| Layer | Technologies |
|---|---|
| **Backend API** | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2 |
| **Database & Cache** | PostgreSQL 16 with `pgvector`, Redis 7 |
| **Worker Queue** | Celery 5.4 + Celery Beat for scheduled accruals & background tasks |
| **Frontend SPA** | React 18, Vite, TypeScript, Tailwind CSS, TanStack Query, Lucide React |
| **AI / Inference** | Local Ollama (`llama3.1:8b`, `qwen2.5:7b`), `nomic-embed-text`, OpenAI fallback |
| **DevOps & Containers** | Docker Compose, multi-stage Dockerfiles, GitHub Actions CI/CD |

---

## Monorepo Structure

```
ai-hr-platform/
├── backend/
│   ├── alembic/              # Async database migration scripts
│   ├── app/
│   │   ├── api/v1/           # API routes (auth, employees, onboarding, policies, leaves, reviews, webhooks)
│   │   ├── core/             # Configuration, database session, security, celery setup
│   │   ├── models/           # SQLAlchemy async models (Base, Org, Employee, Onboarding, Policy, Leave, etc.)
│   │   ├── schemas/          # Pydantic v2 request/response schemas
│   │   ├── services/         # Business logic, PII scrubber, RAG retriever, LLM router
│   │   └── workers/          # Celery background tasks (accrual jobs, review synthesis)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI components (Modals, Tables, Forms, Badges)
│   │   ├── pages/            # View pages (Dashboard, Directory, Leave, Policies, Reviews)
│   │   ├── hooks/            # TanStack Query & custom hooks
│   │   ├── services/         # Axios / fetch API client wrappers
│   │   └── types/            # TypeScript interfaces & domain types
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
├── docker/
│   ├── docker-compose.yml    # Complete local stack (Postgres, Redis, Ollama, Backend, Frontend)
│   └── .env.example          # Environment variable template
├── docs/
│   ├── architecture.md       # Detailed system design, multi-tenancy, and integration architecture
│   ├── erd.md                # Entity Relationship Diagram and schema definitions
│   └── roadmap.md            # Complete 17-milestone phased execution roadmap
└── README.md
```

---

## Quickstart Guide

### Prerequisites
- [Docker Engine & Docker Compose](https://docs.docker.com/get-docker/) (v20.10+)
- [Ollama](https://ollama.com/) (if running models locally outside Docker)

### 1. Clone & Setup Environment
```bash
git clone https://github.com/example/ai-hr-platform.git
cd ai-hr-platform
cp docker/.env.example docker/.env
```

### 2. Launch Stack via Docker Compose
To launch the complete infrastructure (PostgreSQL with `pgvector`, Redis, Ollama, FastAPI Backend, Celery Worker, and React Frontend):

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

### 3. Initialize Local AI Models (Ollama)
Once the Ollama container is healthy, pull the primary LLM and embedding models:
```bash
docker exec -it ai_hr_ollama ollama pull llama3.1:8b
docker exec -it ai_hr_ollama ollama pull nomic-embed-text
```

### 4. Verify Services
- **Backend API Docs (Swagger):** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **Frontend Portal:** [http://localhost:3000](http://localhost:3000)
- **Service Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## Upstream Integration: `ai-recruiter` Webhook

When a candidate accepts an offer in `ai-recruiter`, dispatch an HTTP POST request:

```bash
curl -X POST http://localhost:8000/api/v1/webhooks/recruiter/offer-accepted \
  -H "Content-Type: application/json" \
  -H "X-Recruiter-Signature: sha256=<HMAC_HEX_DIGEST>" \
  -d '{
    "event_id": "evt_100293",
    "event_type": "candidate.offer_accepted",
    "organization_id": "11111111-1111-1111-1111-111111111111",
    "candidate": {
      "recruiter_candidate_id": "cand_9941",
      "first_name": "Marcus",
      "last_name": "Vance",
      "email": "marcus.vance@example.com",
      "job_title": "Full Stack Engineer",
      "department": "Engineering",
      "hire_date": "2026-12-01",
      "employment_type": "FULL_TIME"
    }
  }'
```

---

## Implementation Roadmap

Development is structured into a sequential 17-milestone execution plan. For detailed deliverables, technical specifications, and acceptance criteria for each phase, review [`docs/roadmap.md`](docs/roadmap.md).
