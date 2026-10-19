.PHONY: help install test lint fmt check report clean zip

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies using uv
	uv sync

test: ## Run Appium test suite and generate HTML report
	uv run pytest tests/ -v

report: ## Open standalone HTML report in default browser
	@python3 -m webbrowser "file://$(PWD)/reports/report.html" || open reports/report.html

lint: ## Run code linter and formatting checks
	uv run ruff check pages/ config/ tests/
	uv run ruff format --check pages/ config/ tests/

fmt: ## Automatically format and fix code style
	uv run ruff format pages/ config/ tests/
	uv run ruff check --fix pages/ config/ tests/

check: lint test ## Run both lint and test suite

clean: ## Clean cache and temporary files
	rm -rf .pytest_cache .ruff_cache

zip: clean ## Package clean submission ZIP archive per assignment requirements
	@rm -f ../android-webview-automation.zip
	@zip -r ../android-webview-automation.zip . \
		-x ".venv/*" \
		-x ".git/*" \
		-x ".pytest_cache/*" \
		-x ".ruff_cache/*" \
		-x ".env" \
		-x ".DS_Store" \
		-x "*/.DS_Store" \
		-x "reports/*.log" \
		-x "reports/screenshots/*" \
		-x "__pycache__/*" \
		-x "*/__pycache__/*"
	@echo "Packaged clean submission archive: ../android-webview-automation.zip"
