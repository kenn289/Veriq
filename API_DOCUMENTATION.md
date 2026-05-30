# API Documentation

Base URL: http://localhost:8000
OpenAPI: http://localhost:8000/docs

## GET /api/v1/health

### Request schema
None

### Response schema
```json
{
  "status": "string",
  "timestamp": "string (ISO 8601)"
}
```

### Example response
```json
{
  "status": "ok",
  "timestamp": "2026-05-30T12:00:00+00:00"
}
```

### Error cases
- 500 Internal Server Error
  - Condition: unexpected server error
  - Response: {"detail": "Internal Server Error"}

## GET /api/v1/version

### Request schema
None

### Response schema
```json
{
  "app_name": "string",
  "app_version": "string",
  "environment": "string"
}
```

### Example response
```json
{
  "app_name": "Veriq API",
  "app_version": "0.1.0",
  "environment": "development"
}
```

### Error cases
- 500 Internal Server Error
  - Condition: unexpected server error
  - Response: {"detail": "Internal Server Error"}

## POST /api/v1/auth/register

### Request schema
```json
{
  "tenant_name": "string",
  "tenant_slug": "string | null",
  "organization_name": "string",
  "workspace_name": "string",
  "email": "string",
  "full_name": "string",
  "password": "string"
}
```

### Response schema
```json
{
  "tenant_id": "string",
  "organization_id": "string",
  "workspace_id": "string",
  "user_id": "string"
}
```

### Example response
```json
{
  "tenant_id": "tenant-uuid",
  "organization_id": "org-uuid",
  "workspace_id": "workspace-uuid",
  "user_id": "user-uuid"
}
```

### Error cases
- 400 Bad Request
  - Condition: tenant slug exists or invalid payload
  - Response: {"detail": "Tenant slug already exists"}

## POST /api/v1/auth/login

### Request schema
```json
{
  "tenant_slug": "string",
  "email": "string",
  "password": "string"
}
```

### Response schema
```json
{
  "access_token": "string",
  "token_type": "string",
  "expires_in": "number"
}
```

### Example response
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Error cases
- 401 Unauthorized
  - Condition: invalid credentials
  - Response: {"detail": "Invalid credentials"}

## GET /api/v1/auth/me

### Request schema
None

### Response schema
```json
{
  "user_id": "string",
  "tenant_id": "string",
  "email": "string",
  "full_name": "string",
  "is_active": true
}
```

### Example response
```json
{
  "user_id": "user-uuid",
  "tenant_id": "tenant-uuid",
  "email": "admin@acme.com",
  "full_name": "Admin",
  "is_active": true
}
```

### Error cases
- 401 Unauthorized
  - Condition: missing or invalid token

## GET /api/v1/organizations

### Request schema
None

### Response schema
```json
[
  {"id": "string", "name": "string", "slug": "string"}
]
```

### Example response
```json
[
  {"id": "org-uuid", "name": "QA", "slug": "qa"}
]
```

### Error cases
- 401 Unauthorized

## POST /api/v1/organizations

### Request schema
```json
{
  "name": "string",
  "slug": "string | null"
}
```

### Response schema
```json
{
  "id": "string",
  "name": "string",
  "slug": "string"
}
```

### Example response
```json
{"id": "org-uuid", "name": "QA", "slug": "qa"}
```

### Error cases
- 403 Forbidden
  - Condition: role not permitted
- 409 Conflict
  - Condition: organization slug exists

## GET /api/v1/workspaces

### Request schema
None

### Response schema
```json
[
  {"id": "string", "name": "string", "slug": "string", "organization_id": "string"}
]
```

### Example response
```json
[
  {"id": "workspace-uuid", "name": "Core", "slug": "core", "organization_id": "org-uuid"}
]
```

### Error cases
- 401 Unauthorized

## POST /api/v1/workspaces/organizations/{organization_id}

### Request schema
```json
{
  "name": "string",
  "slug": "string | null"
}
```

### Response schema
```json
{
  "id": "string",
  "name": "string",
  "slug": "string",
  "organization_id": "string"
}
```

### Example response
```json
{"id": "workspace-uuid", "name": "Core", "slug": "core", "organization_id": "org-uuid"}
```

### Error cases
- 403 Forbidden
- 409 Conflict
  - Condition: workspace slug exists

## GET /api/v1/workspaces/{workspace_id}/detail

### Request schema
None

### Response schema
```json
{
  "id": "string",
  "name": "string",
  "slug": "string",
  "organization_id": "string"
}
```

### Example response
```json
{"id": "workspace-uuid", "name": "Core", "slug": "core", "organization_id": "org-uuid"}
```

### Error cases
- 403 Forbidden
- 404 Not Found

## GET /api/v1/projects/workspaces/{workspace_id}

### Request schema
None

### Response schema
```json
[
  {"id": "string", "name": "string", "slug": "string", "workspace_id": "string"}
]
```

### Example response
```json
[
  {"id": "project-uuid", "name": "Web", "slug": "web", "workspace_id": "workspace-uuid"}
]
```

### Error cases
- 403 Forbidden

## POST /api/v1/projects/workspaces/{workspace_id}

### Request schema
```json
{
  "name": "string",
  "slug": "string | null"
}
```

### Response schema
```json
{
  "id": "string",
  "name": "string",
  "slug": "string",
  "workspace_id": "string"
}
```

### Example response
```json
{"id": "project-uuid", "name": "Web", "slug": "web", "workspace_id": "workspace-uuid"}
```

### Error cases
- 403 Forbidden
- 409 Conflict
  - Condition: project slug exists

## Future endpoints
- Test design and generation APIs
- Execution and reporting APIs
