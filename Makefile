.PHONY = lint test format

lint:
	poetry run flake8 .
	poetry run isort --check-only .
	poetry run black --check .
	poetry run mypy .

format:
	poetry run isort .
	poetry run black .

lock: ./pyproject.toml
	poetry lock

dist: src/aws_rss_feed_bot lock
	mkdir -p dist
	poetry export -o dist/requirements.txt --without-hashes
	pip install -r dist/requirements.txt -t dist/
