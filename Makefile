.PHONY: setup lint format

setup:
	@echo "Setting up environment"
	poetry install --with dev,types --sync

lint:
	@echo "Running lint"
	poetry run ruff check ./src ./tests ./scripts
	poetry run mypy ./src ./tests ./scripts

format:
	@echo "Running format"
	poetry run ruff check --fix ./src ./tests ./scripts
	poetry run ruff format ./src ./tests ./scripts

