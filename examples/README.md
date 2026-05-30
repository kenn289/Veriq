# examples

## Purpose
Provide runnable examples and reference flows.

## Responsibilities
- Showcase common workflows
- Demonstrate SDK and CLI usage
- Offer templates for new users

## Architecture Diagram
```mermaid
flowchart TD
  EX[Example] --> RUN[Run]
  RUN --> OUT[Output]
```

## Flow Diagram
```mermaid
flowchart LR
  EX[Example] --> EXEC[Execute]
  EXEC --> RES[Result]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant User as User
  participant Example as Example
  User->>Example: Run example
  Example-->>User: Result
```

## Usage Examples
- Run a sample login test generation.
- Validate execution outputs.

## Troubleshooting
- Confirm environment variables are set.
- Check sample dependencies.
