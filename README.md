# Veriq

From Natural Language to Production-Ready Test Automation.

## Overview
Veriq is an AI-powered autonomous test engineering platform that converts natural language requirements into production-ready test automation across UI, API, and system layers.

## Phase 0 scope
- Monorepo scaffolding with clear module boundaries
- Backend API skeleton with health and version endpoints
- Frontend landing page with a minimal analytics preview
- Docker Compose and CI workflows for repeatable builds

## Quickstart (Docker Compose)
1. Copy .env.example to .env and adjust values.
2. Run docker compose up --build.
3. Open http://localhost:3000 and http://localhost:8000/docs.

## Local development

### Backend
1. cd backend
2. python -m venv .venv
3. .venv\Scripts\activate
4. pip install -e .[dev]
5. uvicorn veriq.main:app --reload

### Frontend
1. cd frontend
2. npm install
3. npm run dev

## Repository structure
- backend/ API services, domain model, and infrastructure
- frontend/ React app and UI
- agents/ AI agent definitions and orchestration
- automation/ framework generation and execution adapters
- healing/ locator healing and self-repair logic
- analytics/ analytics services and dashboards
- ai/ LLM routing, prompts, and evaluators
- integrations/ third-party integrations and webhooks
- browser-extension/ recorder extension
- jenkins-plugin/ Jenkins plugin
- github-app/ GitHub App
- cli/ CLI entrypoint and commands
- sdk/ SDKs for supported languages
- deployment/ deployment guides and manifests
- docker/ Dockerfiles and images
- scripts/ operational scripts
- docs/ extended documentation
- examples/ usage examples
- tests/ shared tests and harnesses
- research/ prototypes and experiments

## Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [ROADMAP.md](ROADMAP.md)
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- [USER_GUIDE.md](USER_GUIDE.md)
- [SECURITY.md](SECURITY.md)
- [AGENT_DESIGN.md](AGENT_DESIGN.md)
- [DATABASE_DESIGN.md](DATABASE_DESIGN.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/api.md](docs/api.md)
- [docs/roadmap.md](docs/roadmap.md)
- [docs/phase-1-auth.md](docs/phase-1-auth.md)
