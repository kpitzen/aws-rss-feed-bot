import os
from distutils.util import strtobool
from typing import Optional


class OpenAIConfig:
    api_key: str

    def __init__(self, api_key: Optional[str] = None):
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get("OPENAI_API_KEY", "")
        if self.api_key == "":
            raise ValueError("No API key provided")


class AWSRSSConfig:
    rss_url: str
    bucket_name: str

    def __init__(
        self, rss_url: Optional[str] = None, bucket_name: Optional[str] = None
    ):
        if rss_url:
            self.rss_url = rss_url
        else:
            self.rss_url = os.environ.get("AWS_RSS_URL", "")
        if self.rss_url == "":
            raise ValueError("No RSS URL provided")
        if bucket_name:
            self.bucket_name = bucket_name
        else:
            self.bucket_name = os.environ.get("AWS_S3_BUCKET_NAME", "")
        if self.bucket_name == "":
            raise ValueError("No bucket name provided")


class Configuration:
    openai_config: OpenAIConfig
    aws_rss_config: AWSRSSConfig
    disable_tty: bool = False

    def __init__(
        self,
        openai_config: Optional[OpenAIConfig] = None,
        aws_rss_config: Optional[AWSRSSConfig] = None,
        disable_tty: Optional[bool] = None,
    ):
        if openai_config:
            self.openai_config = openai_config
        else:
            self.openai_config = OpenAIConfig()
        if aws_rss_config:
            self.aws_rss_config = aws_rss_config
        else:
            self.aws_rss_config = AWSRSSConfig()
        if disable_tty is not None:
            self.disable_tty = disable_tty
        else:
            self.disable_tty = bool(strtobool(os.environ.get("DISABLE_TTY", "False")))
