# Load env vars from .env (optional)
-include .env
export

# --- Config ---
IMAGE_BASE := $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACT_REGISTRY_NAME)/speech-to-text


gcloud-auth:
	gcloud config unset auth/impersonate_service_account
	gcloud auth application-default login --project=$(PROJECT_ID)
	gcloud auth login --project=$(PROJECT_ID)
	gcloud config set project $(PROJECT_ID)

docker-auth:
	gcloud auth configure-docker $(REGION)-docker.pkg.dev

install-precommit:
	uvx pre-commit install

run-precommit:
	uvx pre-commit run --all-files

run-basic-agent:
	cd agents && \
	uv run --group basic-agent adk web --port 8000 --otel_to_cloud 