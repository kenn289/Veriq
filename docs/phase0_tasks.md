Phase 0 — Foundation: Implementation Tasks

- Add product specification (VERIQ_v2 Enterprise) — done (docs/VERIQ_v2_ENTERPRISE_SPEC.md)
- Add backend service stubs: auth, orgs, agents (backend/services/*)
- Add initial database schema (architecture/initial_schema.sql)
- Add basic tests and CI-ready placeholder (tests/test_basic.py)
- Wire incremental commits and push to main

Next steps:
- Implement identity endpoints and JWT auth
- Add DB migrations (Alembic) and models (SQLAlchemy)
- Add OpenAPI skeleton and include routers in application factory
- Implement org/team management endpoints
