# agents

## Purpose
Define AI agent roles, policies, and orchestration logic for Veriq.

## Responsibilities
- Describe agent behaviors and capabilities
- Coordinate multi-agent workflows
- Provide audit and observability metadata

## Architecture Diagram
```mermaid
flowchart TD
  C[Coordinator] --> A[Agent Runtime]
  A --> M[Memory]
  A --> T[Tools]
```

## Flow Diagram
```mermaid
flowchart LR
  I[Input] --> A[Agent]
  A --> O[Output]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant U as User
  participant C as Coordinator
  participant A as Agent
  U->>C: Request
  C->>A: Delegate task
  A-->>C: Result
  C-->>U: Response
```

## Usage Examples
- Add a new agent definition under agents/.
- Update routing rules in the coordinator.

## Troubleshooting
- Validate model credentials and tool permissions.
- Check agent logs for missing context.
