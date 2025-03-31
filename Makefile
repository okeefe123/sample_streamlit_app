# GCP Project and Registry configuration
GCP_PROJECT := load-balancing-experiment
GCP_REGION := us-central1
GCP_REGISTRY := $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT)
APP_NAME := weather-app
VERSION := latest

# Docker Compose configuration
COMPOSE_FILE := docker-compose.yml

.PHONY: help build tag-images push-images run stop clean auth-configure

help: ## Show this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker images using docker-compose
	docker compose -f $(COMPOSE_FILE) build

tag-images: build ## Tag images for GCP Artifact Registry
	docker tag sample_streamlit_app-backend:latest $(GCP_REGISTRY)/$(APP_NAME)/backend:$(VERSION)
	docker tag sample_streamlit_app-frontend:latest $(GCP_REGISTRY)/$(APP_NAME)/frontend:$(VERSION)

push-images: tag-images ## Push images to GCP Artifact Registry
	docker push $(GCP_REGISTRY)/$(APP_NAME)/backend:$(VERSION)
	docker push $(GCP_REGISTRY)/$(APP_NAME)/frontend:$(VERSION)

run: ## Run the application using docker-compose
	docker compose -f $(COMPOSE_FILE) up -d

stop: ## Stop the application
	docker compose -f $(COMPOSE_FILE) down

clean: stop ## Clean up Docker resources
	docker compose -f $(COMPOSE_FILE) down --rmi all --volumes --remove-orphans

auth-configure: ## Configure Docker to use GCP Artifact Registry
	gcloud auth configure-docker $(GCP_REGION)-docker.pkg.dev

deploy: push-images ## Full deployment process
	@echo "Images built and pushed to GCP Artifact Registry"
	@echo "Backend image: $(GCP_REGISTRY)/$(APP_NAME)/backend:$(VERSION)"
	@echo "Frontend image: $(GCP_REGISTRY)/$(APP_NAME)/frontend:$(VERSION)"
	@echo "To deploy to Cloud Run or GKE, additional steps are required."