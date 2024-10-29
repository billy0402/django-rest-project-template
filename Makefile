SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:

MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

PROJECT_NAME=django-rest-project-template

init: env install  ## Init local develop
	pre-commit install --install-hooks
.PHONY: init

env:  ## Setup develop
	@[[ -f .env ]] || sed "s/!!!SECRET_KEY!!!/$$(make secret-key)/g" server/settings/.env.example > server/settings/.env
	@echo '.env.example -> .env'
.PHONY: env

install:  ## Install dependences
	poetry install --sync
.PHONY: install

test:  ## Run check and test
	poetry run python manage.py check
	poetry run pytest -p no:legacypath
.PHONY: test

lint:  ## Check lint
	poetry run ruff check .
	poetry run ruff format --check .
.PHONY: lint

lint-fix:  ## Fix lint
	poetry run ruff check --fix .
	poetry run ruff format .
.PHONY: lint-fix

typecheck:  ## Run typechecking
	PYRIGHT_PYTHON_IGNORE_WARNINGS=1 poetry run pyright .
.PHONY: typecheck

ci: lint typecheck test  ## Run all checks (lint, typecheck, test)
.PHONY: ci

clean:  ## Clean cache files
	find . -name '__pycache__' -type d | xargs rm -rvf
	find . -name '.pytest_cache' -type d | xargs rm -rvf
	find . -name '.DS_Store' -type f | xargs rm -rvf
	rm -rvf htmlcov lcov.info .coverage
	poetry run ruff clean
.PHONY: clean

build:  ## Build Docker image
	docker build -t $(PROJECT_NAME):$$(git rev-parse --short HEAD) -t $(PROJECT_NAME):$$(git rev-parse --abbrev-ref HEAD) -t $(PROJECT_NAME):latest .
.PHONY: build

dev-server: install  ## Run local develop server
	poetry run python manage.py runserver
.PHONY: dev-server

dev-server-plus: install  ## Run local develop server
	poetry run python manage.py runserver_plus --print-sql
.PHONY: dev-server

secret-key:  ## Generate secret key
	@openssl rand -hex 32
.PHONY: secret-key

dev-services-up:  ## Start servers for local dev
	@docker compose -f .devcontainer/docker-compose.yml up -d
.PHONY: dev-services-up

dev-services-down:  ## Stop servers for local dev
	@docker compose -f .devcontainer/docker-compose.yml down
.PHONY: dev-services-down

dev-services-with:  ## Run docker compose with args
	docker compose -f .devcontainer/docker-compose.yml $(args)
.PHONY: dev-services-with

.DEFAULT_GOAL := help
help: Makefile
	@grep -E '(^[a-zA-Z_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'
.PHONY: help
