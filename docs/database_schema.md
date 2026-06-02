# VERIQ Database Schema — Overview

This document describes the initial database schema defined in `architecture/db_schema.sql`. It summarizes each core table, primary keys, important columns, and key relationships. Use this as a developer-facing reference during implementation.

Guidelines
- SQL dialect: Postgres-compatible (uses `gen_random_uuid()` by default).
- Production notes: add appropriate indexes for large tables (e.g., `test_runs`, `test_results`, `analytics_events`) and tune partitioning for high-volume data.

1. Identity / Organizations
- `users` (PK: `id` UUID)
  - Columns: `email` (unique), `full_name`, `hashed_password`, `is_active`, timestamps.
  - Notes: store password hashes with a secure algorithm (bcrypt/argon2). Do not store plaintext.

- `organizations` (PK: `id` UUID)
  - Columns: `name`, `slug` (unique), `created_by` → `users.id`.

- `workspaces` (PK: `id` UUID)
  - Columns: `organization_id` → `organizations.id`, `name`, `slug`, `region`, `billing_plan`.
  - Notes: workspace-level isolation for secrets and usage quotas.

- `roles`, `memberships`
  - `roles` contains role definitions (Owner, Admin, SDET, QA, Viewer, Billing).
  - `memberships` links `users` to `workspaces` with `role_id`.

2. Audit & Security
- `audit_logs` (PK: `id` UUID)
  - Columns: `organization_id`, `workspace_id`, `user_id`, `event_type`, `event_data` (JSONB), `created_at`.
  - Notes: append-only; consider immutable storage or WORM for long-term retention.

- `service_tokens`
  - Per-workspace tokens stored as hashed values; maintain scopes and revocation flags.

3. Agents & Tasks
- `agents` defines agent configurations and types (Coordinator, Requirement, CodeGen, Execution, Healing).
- `tasks` tracks agent jobs and workflows; fields: `type`, `input` (JSONB), `status` (pending/running/completed/failed), `result`, `error`, timestamps.
  - Notes: implement TTL and dead-letter queue behavior for failed tasks.

4. Requirements & Test Plans
- `requirements` stores ingested requirements (NL text, PR diff metadata, Jira references) and `structured` JSONB output from Requirement Agent.
- `test_plans` references `requirements` and contains generated `plan` JSONB and provenance (generated_by, generated_at).

5. Test Cases & Steps
- `test_cases` stores canonical test cases in a workspace, with `priority` and metadata.
- `test_steps` ordered steps for each test case; `action`, `target`, `value`, `position` determine execution.

6. Test Runs & Results
- `test_runs` orchestrates executions; fields: `status` (queued/running/completed), `metadata` (environment), `started_at`, `completed_at`.
- `test_results` stores per-case outcomes: `status`, `duration_seconds`, `error_message`, and `artifacts` (JSONB references).

7. Artifacts
- `artifacts` references storage paths for screenshots, videos, logs, HAR files. Include `type` and `size_bytes` for billing/retention decisions.

8. Coverage & Analytics
- `coverage_reports` stores periodic coverage snapshots (JSONB) per workspace.
- `analytics_events` stores time-series events for dashboards; consider streaming to an OLAP store or data lake for long-term analysis.

9. Billing
- `billing_subscriptions` and `billing_invoices` implement subscription metadata; `meter` JSON tracks usage (executions, storage) to generate invoices.

10. Secrets
- `secrets` stores encrypted secret blobs per workspace. Keys should be encrypted with a KMS (customer-managed where required).

Indexing & Scaling Notes
- Add indexes on `test_runs(workspace_id, status)`, `test_results(test_run_id)`, and `analytics_events(created_at)`.
- Partition high-volume tables (`analytics_events`, `artifacts`, `test_results`) by date or workspace for better performance.

Retention & GDPR
- Provide configurable retention policies for artifacts and analytics. Implement data deletion APIs and processes to comply with GDPR requests.

Next Steps
- Produce an ER diagram (Graphviz/Mermaid) and DDL migration scripts (Alembic) from this schema.
