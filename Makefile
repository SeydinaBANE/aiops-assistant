.PHONY: setup check format test test-no-cov docker-build docker-up docker-down \
        kind-create kind-delete helm-install helm-uninstall ci all help

UV := uv run

# ── Setup ────────────────────────────────────────────────────────────────────

setup:                                                                     ## Install all dependencies + pre-commit hooks
	uv sync --extra dev
	$(UV) pre-commit install

# ── Quality ─────────────────────────────────────────────────────────────────

check:                                                                     ## Run linter + type checker + format check
	$(UV) ruff check src tests
	$(UV) ruff format --check src tests
	$(UV) mypy src

format:                                                                    ## Auto-format code
	$(UV) ruff check --fix src tests
	$(UV) ruff format src tests

# ── Tests ───────────────────────────────────────────────────────────────────

test:                                                                      ## Run tests with coverage
	$(UV) pytest -x

test-no-cov:                                                               ## Run tests without coverage (fast)
	$(UV) pytest -x --no-cov

# ── Frontend ─────────────────────────────────────────────────────────────────

frontend-install:															## Install frontend dependencies
	cd frontend && npm ci

frontend-dev:																## Start frontend dev server
	cd frontend && npm run dev

frontend-build:																## Build frontend for production
	cd frontend && npm ci && npm run build

# ── Docker ──────────────────────────────────────────────────────────────────

docker-build:                                                              ## Build production image
	docker build -t aiops-assistant:latest .

docker-up:                                                                 ## Start full stack locally
	docker compose up --build -d

docker-down:                                                               ## Stop local stack
	docker compose down

docker-logs:                                                               ## View docker compose logs
	docker compose logs -f

# ── Kubernetes ──────────────────────────────────────────────────────────────

kind-create:                                                               ## Create local Kind cluster
	kind create cluster --config k8s/kind-config.yaml 2>/dev/null || true

kind-delete:                                                               ## Delete local Kind cluster
	kind delete cluster

helm-install:                                                              ## Deploy via Helm
	helm upgrade --install aiops-assistant helm/aiops-assistant --namespace aiops --create-namespace

helm-uninstall:                                                            ## Remove Helm release
	helm uninstall aiops-assistant --namespace aiops

# ── CI (full pipeline) ──────────────────────────────────────────────────────

ci: check test                                                             ## Run CI pipeline locally

all: setup check test docker-build                                         ## Everything from scratch

# ── Help ────────────────────────────────────────────────────────────────────

help:                                                                      ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| sort \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
