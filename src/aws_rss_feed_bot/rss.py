from typing import Optional

import feedparser
from pydantic import BaseModel

from aws_rss_feed_bot import configuration


class RSSFeedClient:
    config: configuration.Configuration

    def __init__(self, config: Optional[configuration.Configuration] = None):
        self.configure(config)

    def configure(self, config: Optional[configuration.Configuration]):
        if not config:
            self.config = configuration.Configuration()
        else:
            self.config = config

    @property
    def _feed(self) -> feedparser.FeedParserDict:
        parsed_feed: feedparser.FeedParserDict = feedparser.parse(
            self.config.aws_rss_config.rss_url
        )
        return parsed_feed

    @property
    def latest(self) -> feedparser.FeedParserDict:
        return self._feed.entries[0]


class RSSPublishInfo(BaseModel):
    published: str
    title: str = ""
    link: str = ""
    summary: str = ""
