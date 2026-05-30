# sdk

## Purpose
Provide SDKs for integrating Veriq into existing workflows.

## Responsibilities
- Offer typed SDKs for supported languages
- Wrap API calls with ergonomic helpers
- Support authentication and retries

## Architecture Diagram
```mermaid
flowchart TD
  SDK[SDK] --> API[Veriq API]
  API --> SVC[Services]
```

## Flow Diagram
```mermaid
flowchart LR
  APP[Client App] --> SDK[SDK]
  SDK --> API[API]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant Dev as Developer
  participant SDK as SDK
  participant API as Veriq API
  Dev->>SDK: generate_test()
  SDK->>API: HTTP request
  API-->>SDK: Response
  SDK-->>Dev: Result
```

## Usage Examples
- veriq.generate_test("checkout flow")
- veriq.execute("smoke")

## Troubleshooting
- Verify API keys and endpoints.
- Enable SDK debug logging.
