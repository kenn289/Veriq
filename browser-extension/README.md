# browser-extension

## Purpose
Capture user interactions in the browser and translate them into automation artifacts.

## Responsibilities
- Record clicks, typing, and navigation
- Generate page objects and assertions
- Export workflows to Veriq

## Architecture Diagram
```mermaid
flowchart TD
  REC[Recorder] --> EVT[Events]
  EVT --> GEN[Generator]
  GEN --> OUT[Artifacts]
```

## Flow Diagram
```mermaid
flowchart LR
  U[User Action] --> CAP[Capture]
  CAP --> MAP[Map]
  MAP --> EXP[Export]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant U as User
  participant EXT as Extension
  participant API as Veriq API
  U->>EXT: Interact with app
  EXT->>API: Send event stream
  API-->>EXT: Ack
```

## Usage Examples
- Record a login flow for automation.
- Export page object candidates.

## Troubleshooting
- Check extension permissions.
- Confirm network access to the API.
