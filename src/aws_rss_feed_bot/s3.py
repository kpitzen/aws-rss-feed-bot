import io
import json
import logging
from typing import Optional

import boto3
import botocore
import pendulum

from aws_rss_feed_bot import configuration, rss


class AWSS3Client:
    config: configuration.Configuration
    publish_info: rss.RSSPublishInfo
    publish_filepath = "publish.json"

    def __init__(self, config: Optional[configuration.Configuration] = None):
        self.log = logging.getLogger(__name__)
        self.configure(config)

    def configure(self, config: Optional[configuration.Configuration]):
        if not config:
            self.config = configuration.Configuration()
        else:
            self.config = config

    def get_latest_publish_info(self):
        buffer = io.BytesIO()
        s3 = boto3.client("s3")
        try:
            s3.download_fileobj(
                self.config.aws_rss_config.bucket_name, self.publish_filepath, buffer
            )
        except botocore.exceptions.ClientError:
            return rss.RSSPublishInfo(published="2021-01-01T00:00:00Z")
        buffer.seek(0)
        return rss.RSSPublishInfo.parse_obj(json.loads(buffer.read().decode("utf-8")))

    def reset_checkpoint(self, datetime: str):
        reset_datetime = pendulum.parse(datetime)
        log = self.log.getChild("reset_checkpoint")
        log.info("Resetting checkpoint")
        publish_info = rss.RSSPublishInfo(published=reset_datetime)
        self.checkpoint(publish_info)

    def checkpoint(self, publish_info: rss.RSSPublishInfo):
        log = self.log.getChild("checkpoint")
        log.info(f"Checkpointing to {publish_info.published}")
        s3 = boto3.client("s3")
        buffer = io.BytesIO()
        buffer.write(publish_info.json().encode("utf-8"))
        buffer.seek(0)
        s3.upload_fileobj(
            buffer, self.config.aws_rss_config.bucket_name, self.publish_filepath
        )
