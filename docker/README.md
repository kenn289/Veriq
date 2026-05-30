# docker

## Purpose
Provide container images and build assets for Veriq services.

## Responsibilities
- Define backend and frontend Docker images
- Standardize runtime configuration for containers

## Architecture Diagram
```mermaid
flowchart TD
  DF[Dockerfiles] --> IMG[Images]
  IMG --> RUN[Containers]
```

## Flow Diagram
```mermaid
flowchart LR
  SRC[Source] --> BUILD[Docker Build]
  BUILD --> IMG[Image]
  IMG --> RUN[Container]
```

## Sequence Diagram
```mermaid
sequenceDiagram
  participant Dev as Developer
  participant Docker as Docker
  participant Img as Image
  Dev->>Docker: docker build
  Docker->>Img: create image
  Img-->>Docker: image ready
  Docker-->>Dev: build complete
```

## Usage Examples
- docker build -f docker/backend.Dockerfile .
- docker build -f docker/frontend.Dockerfile .

## Troubleshooting
- Ensure Docker Desktop is running.
- Rebuild without cache if dependencies change.
