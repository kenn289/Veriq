# cli

## Purpose
Provide a command-line interface for Veriq automation workflows.

## Responsibilities
- Generate tests from natural language
- Execute suites and report results
- Heal failures and analyze defects

## Architecture Diagram
```mermaid
flowchart TD
  CLI[CLI] --> API[Veriq API]
  CLI --> LOCAL[Local Runtime]
```

## Flow Diagram
```mermaid
flowchart LR
  CMD[Command] --> RUN[Execute]
  RUN --> OUT[Output]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant U as User
  participant CLI as CLI
  participant API as Veriq API
  U->>CLI: veriq generate
  CLI->>API: Request
  API-->>CLI: Artifacts
  CLI-->>U: Output
```

## Usage Examples
- veriq generate "Verify login fails"
- veriq run --suite smoke

## Troubleshooting
- Ensure API endpoint is reachable.
- Validate CLI configuration files.
