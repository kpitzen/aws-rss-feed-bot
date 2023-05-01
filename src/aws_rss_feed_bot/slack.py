from typing import Any, Dict, List, Optional

from slack_sdk import WebClient

from aws_rss_feed_bot.configuration import Configuration


def bool_to_str(value: bool) -> str:
    """Convert a boolean value to a string"""
    return "" if value else "not "


def format_summary_changes(changes: List[Dict[str, Any]]) -> List[str]:
    """Format a list of changes for Slack"""
    return [
        f"{change['summary']}\n"
        + f"- We believe this change is {bool_to_str(change['breaking'])}breaking\n"
        + f"- We are {change['confidence']}% confident in this analysis"
        for change in changes
    ]


def format_summary_message(summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Format a summary message for Slack"""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"<{summary['link']}|{summary['title']}>",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n".join(
                    summary
                    for summary in format_summary_changes(summary["summary"]["changes"])
                ),
            },
        },
    ]


class SlackClient:
    client: WebClient
    config: Configuration

    def __init__(self, config: Optional[Configuration] = None):
        self.config = config or Configuration()
        self.client = WebClient(token=self.config.slack_token)

    def publish(self, summaries: List[Dict[str, Any]]):
        """Publish summaries to Slack"""
        for summary in summaries:
            self.client.chat_postMessage(
                channel=self.config.slack_channel,
                text="\n".join(
                    [item["summary"] for item in summary["summary"]["changes"]]
                ),
                blocks=format_summary_message(summary),
            )
