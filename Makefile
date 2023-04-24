.PHONY = lint test format

lint:
	poetry run flake8 .
	poetry run isort --check-only .
	poetry run black --check .
	poetry run mypy .

format:
	poetry run isort .
	poetry run black .
