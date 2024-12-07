
check:
	poetry run black --check --color src tests
	poetry run isort --check src tests
	poetry run ruff check .
	poetry run mypy src tests
	poetry run pylint src tests

format:
	poetry run black src tests
	poetry run isort src tests

fix: format
	poetry run ruff . --fix

test:
	poetry run pytest tests
