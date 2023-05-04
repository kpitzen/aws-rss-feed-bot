.PHONY = lint test format docker-build

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
	rm -rf dist
	mkdir -p dist
	poetry export -o dist/requirements.txt --without-hashes
	pip install -r dist/requirements.txt -t dist/

docker-build:
	docker build -t aws-rss-feed-bot \
	  --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} \
	  --build-arg SLACK_BOT_CHANNEL=${SLACK_BOT_CHANNEL} \
	  --build-arg SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN} \
	  --build-arg AWS_RSS_URL=${AWS_RSS_URL} \
	  --build-arg AWS_S3_BUCKET_NAME=${AWS_S3_BUCKET_NAME} \
	  .