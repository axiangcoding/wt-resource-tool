.PHONY: setup lint format

setup:
	@echo "Setting up environment"
	uv sync --group dev --group types

lint:
	@echo "Running lint"
	uv run ruff check ./src ./tests 
	uv run mypy ./src ./tests 

format:
	@echo "Running format"
	uv run ruff check --fix ./src ./tests 
	uv run ruff format ./src ./tests 

test:
	@echo "Running tests"
	uv run pytest ./tests