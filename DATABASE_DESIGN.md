# Database Design

## Goals
- Support multi-tenancy and workspace isolation
- Track executions, artifacts, and healing history
- Enable analytics and risk modeling

## Core entities
- Tenant
- Organization
- Workspace
- Project
- User
- Role
- TestSuite
- TestCase
- Execution
- Artifact
- LocatorHistory

## Entity relationship sketch
```mermaid
erDiagram
  TENANT ||--o{ ORGANIZATION : owns
  ORGANIZATION ||--o{ WORKSPACE : contains
  WORKSPACE ||--o{ PROJECT : contains
  PROJECT ||--o{ TESTSUITE : includes
  TESTSUITE ||--o{ TESTCASE : includes
  PROJECT ||--o{ EXECUTION : runs
  EXECUTION ||--o{ ARTIFACT : produces
  TESTCASE ||--o{ LOCATORHISTORY : tracks
  USER }o--o{ WORKSPACE : member_of
  ROLE }o--o{ USER : assigned
```

## Future considerations
- Partitioning by tenant
- Audit log retention policies
- Encryption at rest and in transit
