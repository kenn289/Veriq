# frontend

## Purpose
The frontend delivers the Veriq user experience for planning, execution, and analytics.

## Responsibilities
- Present dashboards and reports
- Surface agent actions and execution status
- Provide entry points for test generation

## Architecture Diagram
```mermaid
flowchart TD
  UI[React UI] --> API[Backend API]
  UI --> CHARTS[Analytics Views]
```

## Flow Diagram
```mermaid
flowchart LR
  U[User] --> UI[Frontend]
  UI --> API[Backend]
  API --> DB[(PostgreSQL)]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant U as User
  participant UI as Frontend
  participant API as API
  U->>UI: Request action
  UI->>API: HTTP call
  API-->>UI: JSON response
  UI-->>U: Render UI
```

## Usage Examples
- Start dev server: npm run dev
- Build for production: npm run build

## Troubleshooting
- Ensure Node 20+ is installed.
- Run npm install if dependencies are missing.
