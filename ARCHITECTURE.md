# Architecture Overview

## Architecture decisions
- Clean Architecture boundaries for backend
- Domain-first modeling with explicit services
- Event-ready design for future asynchronous workflows
- Multi-tenant, zero-trust posture from the start

## High-level system diagram
```mermaid
flowchart TD
  U[User] --> FE[Frontend]
  FE --> API[Backend API]
  API --> SVC[Application Services]
  SVC --> DOM[Domain]
  SVC --> INF[Infrastructure]
  INF --> DB[(PostgreSQL)]
  INF --> CACHE[(Redis)]
  INF --> OBJ[(S3/MinIO)]
  API --> AG[AI Agents]
  AG --> EXEC[Test Execution]
```

## Data flow
```mermaid
sequenceDiagram
  participant U as User
  participant FE as Frontend
  participant API as API
  participant SVC as Service
  participant DB as DB
  U->>FE: Create request
  FE->>API: Send payload
  API->>SVC: Validate and execute
  SVC->>DB: Persist
  DB-->>SVC: Result
  SVC-->>API: Response
  API-->>FE: JSON
  FE-->>U: UI update
```

## Boundary rules
- API layer depends only on application layer
- Application layer depends on domain abstractions
- Infrastructure implements domain interfaces
- Domain does not depend on other layers

## Future considerations
- Agent orchestration via LangGraph
- Event bus for execution pipelines
- Modular deployment for agents and workers
