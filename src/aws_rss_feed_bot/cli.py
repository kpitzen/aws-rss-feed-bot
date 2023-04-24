import logging

import click

from aws_rss_feed_bot import openai, rss, s3


@click.command()
@click.option("--checkpoint", "-c", default=False, is_flag=True)
def main(checkpoint: bool):
    logging.basicConfig(level="INFO")
    # openapi_client = client.OpenAPIClient()
    s3_client = s3.AWSS3Client()
    rss_client = rss.RSSFeedClient()
    openai_client = openai.OpenAIClient()
    publish_info = s3_client.get_latest_publish_info()
    latest_rss = rss_client.latest_content_text
    summary = openai_client.summarize(latest_rss)
    logging.info(summary["choices"][0]["text"])

    logging.info(publish_info)
    if checkpoint:
        logging.info("Checkpointing...")
        s3_client.checkpoint(publish_info)
