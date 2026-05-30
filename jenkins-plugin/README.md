# jenkins-plugin

## Purpose
Integrate Veriq execution and reporting into Jenkins pipelines.

## Responsibilities
- Trigger Veriq test runs from Jenkins
- Publish results and artifacts
- Support pipeline configuration

## Architecture Diagram
```mermaid
flowchart TD
  J[Jenkins] --> PL[Plugin]
  PL --> API[Veriq API]
```

## Flow Diagram
```mermaid
flowchart LR
  JOB[Job] --> RUN[Trigger]
  RUN --> RES[Results]
  RES --> PUB[Publish]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant J as Jenkins
  participant P as Plugin
  participant API as Veriq API
  J->>P: Execute build step
  P->>API: Start run
  API-->>P: Run id
  P-->>J: Status
```

## Usage Examples
- Add a pipeline step to trigger Veriq.
- Archive test reports in Jenkins.

## Troubleshooting
- Validate API credentials.
- Check Jenkins plugin logs.
