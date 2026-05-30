# analytics

## Purpose
Provide analytics services and metrics for Veriq dashboards.

## Responsibilities
- Aggregate execution metrics and trends
- Compute quality and risk KPIs
- Serve analytics data to the frontend

## Architecture Diagram
```mermaid
flowchart TD
  EX[Executions] --> AGG[Aggregation]
  AGG --> KPI[KPIs]
  KPI --> UI[Dashboards]
```

## Flow Diagram
```mermaid
flowchart LR
  D[Data] --> P[Processing]
  P --> M[Metrics]
  M --> V[Visualization]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant FE as Frontend
  participant API as Analytics API
  participant DB as Database
  FE->>API: Request metrics
  API->>DB: Query aggregates
  DB-->>API: Results
  API-->>FE: Metrics payload
```

## Usage Examples
- Add new metric aggregations for dashboards.
- Extend trend analysis queries.

## Troubleshooting
- Validate aggregation jobs are running.
- Check data freshness windows.
