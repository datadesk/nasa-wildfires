.DEFAULT_GOAL := help

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_-]+:.*## / {printf "%-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install everything needed for development
	uv sync --all-groups

lint: ## Check code with ruff
	uv run ruff check
	uv run ruff format --check

fix: ## Fix lint problems and format the code
	uv run ruff check --fix
	uv run ruff format

type-check: ## Check types with ty
	uv run ty check

test: ## Run the offline tests
	uv run pytest

test-live: ## Run the tests that call NASA's real website
	uv run pytest -m live

check: lint type-check test ## Run lint, type check and offline tests

build: ## Build the source and wheel files (does not upload anything)
	rm -rf dist
	uv build --sdist --wheel
	uv run twine check dist/*

docs: ## Build the documentation
	uv run sphinx-build -M html docs docs/_build

clean: ## Remove generated files
	rm -rf build dist docs/_build .pytest_cache .ruff_cache
