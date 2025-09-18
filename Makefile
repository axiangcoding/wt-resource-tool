.PHONY: setup lint format

setup:
	@echo "Setting up environment"
	uv sync --group dev --group types

lint:
	@echo "Running lint"
	uv run ruff check ./src ./tests ./scripts
	uv run mypy ./src ./tests ./scripts

format:
	@echo "Running format"
	uv run ruff check --fix ./src ./tests ./scripts
	uv run ruff format ./src ./tests ./scripts

