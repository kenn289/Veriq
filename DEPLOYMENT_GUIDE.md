# Deployment Guide

## Local Docker Compose
1. Copy .env.example to .env.
2. Run docker compose up --build.
3. Access API docs at http://localhost:8000/docs.
4. Access frontend at http://localhost:3000.

## Environment configuration
- VERIQ_DATABASE_URL for PostgreSQL
- VERIQ_REDIS_URL for Redis
- VERIQ_MINIO_ENDPOINT for object storage

## Production notes
- Use managed Postgres and Redis
- Configure TLS and reverse proxy
- Enable audit logging
- Restrict credentials via secrets manager
