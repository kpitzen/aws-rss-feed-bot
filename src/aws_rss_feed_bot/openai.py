import logging
from typing import Optional

import openai
import tiktoken

from aws_rss_feed_bot import configuration


def get_max_tokens(content: str, model: str = "davinci", max_tokens: int = 512):
    encoding = tiktoken.encoding_for_model(model)
    return min(2049 - len(encoding.encode(content)), max_tokens)


class OpenAIClient:
    config: configuration.Configuration
    summary_prompt = """
    Please summarize the following blog post in 3-5 sentences:
    Blog post: {content}
    """
    base_prompt = """
    For this prompt, imagine you are a senior software engineer at a company which builds
    automation tools for provisioning infrastructure on AWS. You are tasked with writing a
    summary about how the announcement in the AWS RSS feed below affects your company's
    technology. This summary should be between 3 and 5 sentences in length, and should be focused
    on whether or not the announcement could result in a breaking change to users of the company's product.
    The content of the blog post is as follows: {content}
    """

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

    def summarize(self, content: str):
        summary_prompt = self.summary_prompt.format(content=content)
        logging.info(summary_prompt)
        summary_response = self.openai.Completion.create(
            engine="davinci",
            prompt=summary_prompt,
            temperature=0.5,
            max_tokens=get_max_tokens(summary_prompt),
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        logging.info(summary_response)
        analysis_prompt = self.base_prompt.format(
            content=summary_response.choices[0].text
        )
        logging.info(analysis_prompt)
        analysis_response = self.openai.Completion.create(
            engine="davinci",
            prompt=analysis_prompt,
            temperature=0.7,
            max_tokens=get_max_tokens(analysis_prompt),
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        logging.info(analysis_response)
        return analysis_response
