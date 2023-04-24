import click

from aws_rss_feed_bot import s3


@click.command()
@click.option("--checkpoint", "-c", default=False, is_flag=True)
def main(checkpoint: bool):
    # openapi_client = client.OpenAPIClient()
    s3_client = s3.AWSS3Client()
    publish_info = s3_client.get_latest_publish_info()
    print(publish_info)
    if checkpoint:
        print("Checkpointing...")
        s3_client.checkpoint(publish_info)
