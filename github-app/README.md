# github-app

## Purpose
Provide GitHub-native workflows for PR analysis and test recommendations.

## Responsibilities
- Monitor pull requests and changes
- Generate impacted tests and risk scores
- Post reports and status checks

## Architecture Diagram
```mermaid
flowchart TD
  GH[GitHub] --> APP[GitHub App]
  APP --> API[Veriq API]
```

## Flow Diagram
```mermaid
flowchart LR
  PR[Pull Request] --> EVT[Event]
  EVT --> ANA[Analyze]
  ANA --> REP[Report]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant GH as GitHub
  participant APP as App
  participant API as Veriq API
  GH->>APP: PR event
  APP->>API: Impact analysis
  API-->>APP: Risk score
  APP-->>GH: Status check
```

## Usage Examples
- Enable Veriq checks on PRs.
- Generate targeted regression suites.

## Troubleshooting
- Verify webhook delivery.
- Confirm GitHub App permissions.
