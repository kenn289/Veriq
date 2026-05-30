# Phase 2 - Test Design & Execution

## Overview
Phase 2 implements test case design, execution, and result tracking APIs. Tests are scoped to workspaces and can be created, run, and tracked through multiple execution cycles.

## Architecture Decisions
- Test Cases exist at workspace level (scoped isolation)
- Test Steps define sequential actions and assertions
- Test Runs track bulk executions (batch or scheduled)
- Test Results store granular pass/fail/error states
- Status tracking enables real-time monitoring

## Data Model

### TestCase
- `id` (UUID): Primary key
- `workspace_id` (UUID): FK - workspace this test belongs to
- `name` (string): Human-readable test name
- `description` (text): Detailed description
- `slug` (string): URL-friendly identifier
- `status` (enum): active, archived, draft
- `priority` (integer): 1-5, for prioritization
- `created_at`, `updated_at`: Timestamps

### TestStep
- `id` (UUID): Primary key
- `test_case_id` (UUID): FK - parent test case
- `order` (integer): Execution sequence
- `action` (string): Action type (click, input, assert, navigate, etc.)
- `target` (string): Element selector or identifier
- `value` (string): Input value or expected output
- `description` (text): Step description
- `created_at`, `updated_at`: Timestamps

### TestRun
- `id` (UUID): Primary key
- `workspace_id` (UUID): FK - workspace
- `name` (string): Run name (e.g., "Nightly Run #42")
- `status` (enum): pending, in_progress, completed, failed
- `total_count` (integer): Total tests in this run
- `passed_count` (integer): Tests passed
- `failed_count` (integer): Tests failed  
- `error_count` (integer): Tests with errors
- `started_at` (datetime): When run started
- `completed_at` (datetime): When run completed
- `duration_seconds` (integer): Total duration
- `created_at`, `updated_at`: Timestamps

### TestResult
- `id` (UUID): Primary key
- `test_run_id` (UUID): FK - parent test run
- `test_case_id` (UUID): FK - which test case
- `status` (enum): passed, failed, error, skipped
- `duration_seconds` (integer): Execution time
- `error_message` (text): Failure/error details
- `error_stack_trace` (text): Full stack trace if available
- `failure_step_id` (UUID): Which step failed (if applicable)
- `failure_screenshot` (string): URL to screenshot if available
- `attempts` (integer): Retry count
- `created_at`, `updated_at`: Timestamps

## API Endpoints

### Test Cases
- `GET /api/v1/test_cases?workspace_id=...` - List test cases
- `POST /api/v1/test_cases` - Create test case
  ```json
  {
    "workspace_id": "uuid",
    "name": "Login flow",
    "description": "Verify user login works",
    "priority": 1
  }
  ```
- `GET /api/v1/test_cases/{test_case_id}` - Get details
- `PUT /api/v1/test_cases/{test_case_id}` - Update test case
- `DELETE /api/v1/test_cases/{test_case_id}` - Archive/delete

### Test Steps
- `GET /api/v1/test_cases/{test_case_id}/steps` - List steps
- `POST /api/v1/test_cases/{test_case_id}/steps` - Add step
  ```json
  {
    "action": "click",
    "target": "button.login",
    "description": "Click login button"
  }
  ```
- `PUT /api/v1/test_cases/{test_case_id}/steps/{step_id}` - Update step
- `DELETE /api/v1/test_cases/{test_case_id}/steps/{step_id}` - Delete step

### Test Runs
- `GET /api/v1/test_runs?workspace_id=...` - List runs
- `POST /api/v1/test_runs` - Create/start run
  ```json
  {
    "workspace_id": "uuid",
    "name": "Nightly Run",
    "test_case_ids": ["uuid1", "uuid2"]
  }
  ```
- `GET /api/v1/test_runs/{test_run_id}` - Get run details
- `POST /api/v1/test_runs/{test_run_id}/execute` - Start execution
- `POST /api/v1/test_runs/{test_run_id}/stop` - Stop execution

### Test Results
- `GET /api/v1/test_runs/{test_run_id}/results` - List results
- `POST /api/v1/test_runs/{test_run_id}/results` - Report result
  ```json
  {
    "test_case_id": "uuid",
    "status": "passed",
    "duration_seconds": 45
  }
  ```
- `GET /api/v1/test_results/{result_id}` - Get result details

## Folder Structure
```
backend/veriq/
├── domain/models/
│   ├── test_case.py          # TestCase domain model
│   ├── test_step.py          # TestStep domain model
│   ├── test_run.py           # TestRun domain model
│   └── test_result.py        # TestResult domain model
├── infrastructure/db/
│   └── models.py             # Add ORM models to existing
├── infrastructure/repositories/
│   ├── test_case_repository.py
│   ├── test_step_repository.py
│   ├── test_run_repository.py
│   └── test_result_repository.py
├── application/services/
│   ├── test_case_service.py
│   ├── test_run_service.py
│   └── test_result_service.py
└── api/v1/
    ├── routes/
    │   ├── test_cases.py
    │   ├── test_steps.py
    │   ├── test_runs.py
    │   └── test_results.py
    └── schemas/
        ├── test_case.py
        ├── test_step.py
        ├── test_run.py
        └── test_result.py
```

## Database Migration
New Alembic migration will create tables:
- `test_cases` - Test definitions
- `test_steps` - Sequential test steps
- `test_runs` - Test execution batches
- `test_results` - Individual test outcomes

## Status Tracking
Test lifecycle:
- **Test Case**: draft → active → archived
- **Test Run**: pending → in_progress → completed (or failed)
- **Test Result**: pending → passed/failed/error/skipped

## Integration Points
- Workspace scoping: Tests belong to workspace
- User permissions: Must have access to workspace
- RBAC: Manager/QA Lead can create/run tests
- Slug-based lookups: Friendly URLs

## Testing Strategy
- Unit tests for slug generation, status validation
- Integration tests for CRUD operations
- Full workflow tests: create test → run → verify results

## Next Phases
- Phase 3: AI Test Generation (generate tests from requirements)
- Phase 4: Test Execution Engine (actually execute tests)
- Phase 5+: Advanced features (healing, analysis, CI/CD integration)
