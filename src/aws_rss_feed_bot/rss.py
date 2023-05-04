from typing import List, Optional, Union

import feedparser
import pendulum
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from aws_rss_feed_bot import configuration


class RSSPublishInfo(BaseModel):
    published: Union[pendulum.DateTime, pendulum.Date, pendulum.Time, pendulum.Duration]
    title: str = ""
    link: str = ""
    summary: str = ""

    @classmethod
    def from_entry(cls, entry: feedparser.FeedParserDict):
        return cls(
            published=pendulum.parse(entry["published"], strict=False),
            title=entry["title"],
            link=entry["link"],
            summary=entry["summary"],
        )


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
        return [
            {**entry, "published": pendulum.parse(entry["published"], strict=False)}
            for entry in self._feed.entries
        ]

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

    def entries_to_load(
        self, previous_publish_info: Optional[RSSPublishInfo] = None, lookback: int = 1
    ):
        published_date = (
            previous_publish_info.published
            if previous_publish_info
            else pendulum.parse("2021-01-01T00:00:00Z")
        )
        return [entry for entry in self.entries if entry["published"] > published_date][
            :lookback
        ]

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
