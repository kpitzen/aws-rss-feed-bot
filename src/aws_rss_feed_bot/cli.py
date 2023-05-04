import logging

import click
import pendulum

from aws_rss_feed_bot import openai, rss, s3, slack, utils


@click.command()
@click.option(
    "--checkpoint",
    "-c",
    default=False,
    is_flag=True,
    help="Whether to use checkpoint data from S3 to determine the last published entry",
)
@click.option(
    "--verbosity",
    "-v",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING"]),
    help="Logging level to print",
)
@click.option(
    "--lookback",
    "-l",
    default=1,
    type=click.IntRange(1, 20),
    help="Number of posts to look back on",
)
@click.option(
    "--slack-publish",
    "-s",
    default=False,
    is_flag=True,
    help="Publish summaries to Slack",
)
@click.option(
    "--reset-checkpoint",
    "-r",
    default=False,
    is_flag=True,
    help="Reset checkpoint to default",
)
@click.option(
    "--reset-datetime",
    default="2021-01-01T00:00:00Z",
    help="Reset checkpoint to this datetime [2021-01-01T00:00:00Z]",
)
def main(
    checkpoint: bool,
    verbosity: str,
    lookback: int,
    slack_publish: bool,
    reset_checkpoint: bool,
    reset_datetime: str,
):
    summaries = []
    logging.basicConfig(level=verbosity)
    log = logging.getLogger(__name__)
    s3_client = s3.AWSS3Client()
    rss_client = rss.RSSFeedClient()
    openai_client = openai.OpenAIClient()
    if reset_checkpoint:
        log.info("Resetting checkpoint...")
        s3_client.reset_checkpoint(reset_datetime)
        return
    if checkpoint:
        publish_info = s3_client.get_latest_publish_info()
        log.info(
            f"Using checkpoint to determine posts to summarize since {publish_info.published}"
        )
    else:
        publish_info = rss.RSSPublishInfo(
            published=pendulum.parse("2021-01-01T00:00:00")
        )
        log.info(
            f"Using default publish info to determine posts to summarize since {publish_info.published}"
        )
    if not rss_client.entries_to_load(publish_info, lookback):
        log.info("No new posts to summarize")
        return

    for entry in rss_client.entries_to_load(publish_info, lookback):
        log.info(f"Post link: {entry['link']}")
        summary = openai_client.summarize(rss_client.cleaned_entry(entry))
        log.debug(summary)
        summaries.append(utils.merge_post_with_summary(entry, summary))

    new_publish_info = rss.RSSPublishInfo.from_entry(rss_client.latest)

    log.debug(new_publish_info)
    if checkpoint:
        log.info("Checkpointing...")
        s3_client.checkpoint(new_publish_info)
    if slack_publish:
        log.info("Sending to Slack...")
        slack_client = slack.SlackClient()
        slack_client.publish(summaries)
