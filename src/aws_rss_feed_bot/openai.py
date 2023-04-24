from typing import Optional

import openai

from aws_rss_feed_bot import configuration


class OpenAIClient:
    config: configuration.Configuration

    def __init__(self, config: Optional[configuration.Configuration] = None):
        self.configure(config)

    @property
    def openai(self):
        return openai

    def configure(self, config: Optional[configuration.Configuration]):
        if not config:
            self.config = configuration.Configuration()
        else:
            self.config = config
        openai.api_key = self.config.openai_config.api_key
