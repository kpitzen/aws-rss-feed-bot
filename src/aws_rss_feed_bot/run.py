import logging

import pendulum

from aws_rss_feed_bot import openai, rss, s3, slack, utils


def run_summaries(
    checkpoint: bool = True,
    verbosity: str = "INFO",
    lookback: int = 20,
    slack_publish: bool = True,
    reset_checkpoint: bool = False,
    reset_datetime: str = "2021-01-01T00:00:00Z",
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
    new_publish_info = publish_info
    for entry in rss_client.entries_to_load(publish_info, lookback):
        log.info(f"Post published: {entry['published']}")
        if entry["published"] <= publish_info.published:
            continue
        else:
            if entry["published"] > new_publish_info.published:
                new_publish_info = rss.RSSPublishInfo.from_entry(entry)
        log.info(f"Post link: {entry['link']}")
        summary = openai_client.summarize(rss_client.cleaned_entry(entry))
        log.debug(summary)
        summaries.append(utils.merge_post_with_summary(entry, summary))

    log.debug(new_publish_info)
    if checkpoint:
        log.info("Checkpointing...")
        s3_client.checkpoint(new_publish_info)
    if slack_publish:
        log.info("Sending to Slack...")
        slack_client = slack.SlackClient()
        slack_client.publish(summaries)
