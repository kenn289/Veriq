# ai

## Purpose
Centralize AI model routing, prompts, and evaluation logic.

## Responsibilities
- Select models based on task and policy
- Manage prompt templates and guardrails
- Track evaluation metrics and cost usage

## Architecture Diagram
```mermaid
flowchart TD
  REQ[Request] --> R[Router]
  R --> M[Model]
  M --> E[Evaluation]
```

## Flow Diagram
```mermaid
flowchart LR
  I[Input] --> P[Prompt]
  P --> M[Model]
  M --> O[Output]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant A as Agent
  participant R as Router
  participant M as Model
  A->>R: Task
  R->>M: Prompt
  M-->>R: Completion
  R-->>A: Output
```

## Usage Examples
- Add a new model provider adapter.
- Update prompt templates for test design.

## Troubleshooting
- Check model credentials and quotas.
- Review evaluation logs for failures.
