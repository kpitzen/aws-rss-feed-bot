FROM python:3.11.0

ARG YOUR_ENV

ARG AWS_RSS_URL="https://aws.amazon.com/about-aws/whats-new/recent/feed/"
ARG AWS_S3_BUCKET_NAME="aws-blog-rss-feed-66a9dd0"

ARG OPENAI_API_KEY

ARG SLACK_BOT_TOKEN
ARG SLACK_BOT_CHANNEL

ENV AWS_RSS_URL=$AWS_RSS_URL
ENV AWS_S3_BUCKET_NAME=$AWS_S3_BUCKET_NAME
ENV OPENAI_API_KEY=$OPENAI_API_KEY

ENV SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN
ENV SLACK_BOT_CHANNEL=$SLACK_BOT_CHANNEL

ENV PATH=$HOME/.local/bin:$PATH

RUN apt-get update && \
  apt-get install -y \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev

RUN pip install --upgrade pip
RUN pip install poetry

WORKDIR /app
ADD pyproject.toml poetry.lock /app/
ADD bin/aws-lambda-rie-x86_64 /usr/local/bin/aws-lambda-rie

RUN poetry config virtualenvs.create false \
  && poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") --no-interaction --no-ansi --no-root

ADD . /app

RUN poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["aws_rss_feed_bot.handler.handler"]
