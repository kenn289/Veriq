# docs

## Purpose
Store extended documentation and diagrams for Veriq.

## Responsibilities
- Maintain deep-dive documentation
- Host architecture and API notes
- Track roadmap discussions

## Architecture Diagram
```mermaid
flowchart TD
  D[Docs] --> A[Architecture]
  D --> API[API Notes]
  D --> R[Roadmap]
```

## Flow Diagram
```mermaid
flowchart LR
  W[Write] --> R[Review]
  R --> P[Publish]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant Author as Author
  participant Docs as Docs
  Author->>Docs: Update documentation
  Docs-->>Author: Published
```

## Usage Examples
- Add diagrams for new subsystems.
- Update API notes after changes.
- Review phase details in docs/phase-1-auth.md.

## Troubleshooting
- Ensure links point to current files.
- Keep diagrams in sync with code.
