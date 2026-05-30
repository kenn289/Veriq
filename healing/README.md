# healing

## Purpose
Detect and repair broken locators and flaky tests.

## Responsibilities
- Track locator history and confidence scores
- Apply similarity and AI prediction strategies
- Record healing decisions for audits

## Architecture Diagram
```mermaid
flowchart TD
  L[Locator Failure] --> H[Healing Engine]
  H --> C[Confidence Model]
  H --> S[Suggested Locator]
```

## Flow Diagram
```mermaid
flowchart LR
  F[Failure] --> A[Analyze]
  A --> H[Heal]
  H --> R[Record]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant E as Execution
  participant H as Healing
  participant R as Repository
  E->>H: Locator failure
  H->>R: Search history
  R-->>H: Candidates
  H-->>E: Healing suggestion
```

## Usage Examples
- Run locator healing after failed UI tests.
- Review healing history for audit trails.

## Troubleshooting
- Ensure DOM snapshots are captured.
- Verify similarity thresholds.
