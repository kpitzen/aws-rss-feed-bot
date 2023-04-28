from typing import List, Optional

import feedparser
import requests
from bs4 import BeautifulSoup
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

    @property
    def entries(self) -> List[feedparser.FeedParserDict]:
        return self._feed.entries

    def cleaned_entry(self, entry):
        text_content = (
            BeautifulSoup(self.entry_content(entry), "html.parser")
            .get_text()
            .split("\n\n")
        )
        return "\n".join(
            [paragraph.strip() for paragraph in text_content if paragraph.strip()]
        )

    def entry_content(self, entry: feedparser.FeedParserDict) -> str:
        response = requests.get(entry["link"])
        return response.text

    @property
    def latest_content(self) -> str:
        response = requests.get(self.latest["link"])
        return response.text

    @property
    def latest_content_text(self) -> str:
        text_content = (
            BeautifulSoup(self.latest_content, "html.parser").get_text().split("\n\n")
        )
        return "\n".join(
            [paragraph.strip() for paragraph in text_content if paragraph.strip()]
        )


class RSSPublishInfo(BaseModel):
    published: str
    title: str = ""
    link: str = ""
    summary: str = ""
