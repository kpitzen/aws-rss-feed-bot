import click

from aws_rss_feed_bot.run import run_summaries


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
    run_summaries(
        checkpoint, verbosity, lookback, slack_publish, reset_checkpoint, reset_datetime
    )


if __name__ == "__main__":
    main()
