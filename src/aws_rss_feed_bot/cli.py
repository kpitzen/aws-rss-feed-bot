import logging

import click

from aws_rss_feed_bot import openai, rss, s3


@click.command()
@click.option("--checkpoint", "-c", default=False, is_flag=True)
@click.option(
    "--verbosity", "-v", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING"])
)
def main(checkpoint: bool, verbosity: str):
    logging.basicConfig(level=verbosity)
    log = logging.getLogger(__name__)
    # openapi_client = client.OpenAPIClient()
    s3_client = s3.AWSS3Client()
    rss_client = rss.RSSFeedClient()
    openai_client = openai.OpenAIClient()
    publish_info = s3_client.get_latest_publish_info()
    latest_rss = rss_client.latest_content_text
    summary = openai_client.summarize(latest_rss)
    log.info(summary)

    log.debug(publish_info)
    if checkpoint:
        logging.info("Checkpointing...")
        s3_client.checkpoint(publish_info)
