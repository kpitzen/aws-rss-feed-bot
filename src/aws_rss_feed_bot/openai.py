import logging
from typing import List, Optional

import openai
import tiktoken
from tqdm import tqdm

from aws_rss_feed_bot import configuration


def get_max_tokens(content: str, model: str = "davinci", max_tokens: int = 512):
    encoding = tiktoken.encoding_for_model(model)
    return min(2049 - len(encoding.encode(content)), max_tokens)


def format_summary_response(response: str) -> str:
    return response.strip().replace("\n", " ").replace("  ", " ").replace('"', "")


class OpenAIClient:
    config: configuration.Configuration
    summary_prompt = """
    Please summarize the following paragraph as if you were a senior software engineer
    Your summary should be between 2 and 4 sentences in length.
    Paragraph: \"{paragraph}\"
    Summary:"""
    base_prompt = """
    You are a senior software engineer at a company which builds
    automation tools for provisioning infrastructure on AWS. You are tasked with writing a
    summary about how the announcements in the content below affects your company's
    technology. This summary should be between 1 and 3 sentences in length for each change, and should be focused
    on whether or the announcement is a net-new feature or a breaking change for the company's product.
    Please provide your analysis in the form of a bulleted list with a corresponding percentage representing
    your confidence for each.
    Content: \"{content}\"
    Analysis:"""

    def __init__(self, config: Optional[configuration.Configuration] = None):
        self.log = logging.getLogger(__name__)
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

    def summarize(self, content: List[str]):
        log = self.log.getChild("summarize")
        summary_responses = []
        log.info("Summarizing content...")
        for paragraph in tqdm(content, "Paragraphs: ", disable=self.config.disable_tty):
            summary_prompt = self.summary_prompt.format(
                paragraph=paragraph,
            ).strip()
            log.debug(summary_prompt)
            summary_response = self.openai.Completion.create(
                engine="davinci",
                prompt=summary_prompt,
                temperature=0.1,
                max_tokens=get_max_tokens(summary_prompt),
                frequency_penalty=1.0,
                presence_penalty=0.5,
                stop=["\n\n", "\n"],
            )
            log.debug(summary_response)
            if summary_response["choices"][0]["finish_reason"] == "length":
                raise RuntimeError(
                    "Summary was too long and OpenAI returned an incorrect response."
                )
            summary_responses.append(summary_response.choices[0]["text"])
        cleaned_summary_responses = " ".join(
            [
                format_summary_response(summary_response)
                for summary_response in summary_responses
            ]
        )
        analysis_prompt = self.base_prompt.format(
            content=cleaned_summary_responses
        ).strip()
        log.debug(analysis_prompt)
        log.info("Analyzing summary...")
        analysis_response = self.openai.Completion.create(
            engine="davinci",
            prompt=analysis_prompt,
            temperature=0.1,
            frequency_penalty=1.0,
            presence_penalty=0.5,
            max_tokens=get_max_tokens(analysis_prompt),
        )
        log.debug(analysis_response)
        return analysis_response["choices"][0]["text"]
