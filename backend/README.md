# backend

## Purpose
The backend provides the Veriq API, orchestration foundation, and core services required for autonomous test engineering.

## Responsibilities
- Expose REST APIs and OpenAPI documentation
- Enforce clean architecture boundaries
- Manage configuration, database, cache, and task queues

## Architecture Diagram
```mermaid
flowchart TD
  API[API Layer] --> APP[Application Services]
  APP --> DOM[Domain]
  APP --> INF[Infrastructure]
```

## Flow Diagram
```mermaid
flowchart LR
  U[Client] --> API[API]
  API --> SVC[Service]
  SVC --> DB[(PostgreSQL)]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant U as User
  participant API as API
  participant S as Service
  participant D as DB
  U->>API: Request
  API->>S: Execute use case
  S->>D: Query
  D-->>S: Result
  S-->>API: Response
  API-->>U: 200 OK
```

## Usage Examples
- Start the API: uvicorn veriq.main:app --reload
- Call health: GET /api/v1/health

## Troubleshooting
- Check VERIQ_DATABASE_URL if DB connectivity fails.
- Ensure Redis is running for Celery broker settings.
