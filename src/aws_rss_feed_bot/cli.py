import logging

import click

from aws_rss_feed_bot import openai, rss, s3


@click.command()
@click.option("--checkpoint", "-c", default=False, is_flag=True)
@click.option(
    "--verbosity", "-v", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING"])
)
@click.option(
    "--lookback",
    "-l",
    default=1,
    type=click.IntRange(1, 20),
    help="Number of posts to look back on",
)
def main(checkpoint: bool, verbosity: str, lookback: int):
    logging.basicConfig(level=verbosity)
    log = logging.getLogger(__name__)
    s3_client = s3.AWSS3Client()
    rss_client = rss.RSSFeedClient()
    openai_client = openai.OpenAIClient()
    publish_info = s3_client.get_latest_publish_info()
    for entry in rss_client.entries[:lookback]:
        log.info(f"Post link: {entry['link']}")
        summary = openai_client.summarize(rss_client.cleaned_entry(entry))
        log.info(summary)

    log.debug(publish_info)
    if checkpoint:
        logging.info("Checkpointing...")
        s3_client.checkpoint(publish_info)
