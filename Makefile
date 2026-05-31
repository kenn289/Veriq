.PHONY: build worker-build push push-worker compose-up compose-down

# Registry and image names. Export DOCKER_REGISTRY and DOCKER_USERNAME or rely on docker login.
REGISTRY ?= docker.io
DOCKER_USERNAME ?= $(shell echo)
WEB_IMAGE ?= $(REGISTRY)/$(DOCKER_USERNAME)/veriq-web
WORKER_IMAGE ?= $(REGISTRY)/$(DOCKER_USERNAME)/veriq-worker

build:
	docker build -f backend/Dockerfile -t $(WEB_IMAGE):latest backend

worker-build:
	docker build -f backend/Dockerfile.playwright -t $(WORKER_IMAGE):latest backend

push: build
	docker push $(WEB_IMAGE):latest

push-worker: worker-build
	docker push $(WORKER_IMAGE):latest

upload-signatures:
	# Usage: make upload-signatures IMAGE=yourregistry/your/image TAG=sha
	@[ -z "$(IMAGE)" ] && echo "Set IMAGE and TAG variables (e.g. IMAGE=... TAG=...)" && exit 1 || true
	./scripts/upload_provenance.sh "${IMAGE}" "${TAG}"

verify-upload:
	# Usage: make verify-upload IMAGE=registry/org/name TAG=sha
	@[ -z "$(IMAGE)" ] && echo "Set IMAGE and TAG variables (e.g. IMAGE=... TAG=...)" && exit 1 || true
	./scripts/upload_provenance.sh "${IMAGE}" "${TAG}"

compose-up:
	docker compose up --build

compose-down:
	docker compose down
