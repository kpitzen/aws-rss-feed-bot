import json
import logging
from typing import Optional

import openai
import tiktoken

from aws_rss_feed_bot import configuration


def get_max_tokens(content: str, model: str = "davinci", max_tokens: int = 512):
    encoding = tiktoken.encoding_for_model(model)
    return min(2049 - len(encoding.encode(content)), max_tokens)


def format_summary_response(response: str) -> str:
    return response.strip().replace("'", '"')


class OpenAIClient:
    config: configuration.Configuration
    system_prompt = """
    You are a senior software engineer at a company which builds
    automation tools for provisioning infrastructure on AWS. You are tasked with writing a
    summary about how the announcements in the content below affects your company's
    technology. This summary should be between one and three sentences in length for each change, and should be focused
    on whether or the announcement is a net-new feature or a change to existing functionality which
    the company's tooling interacts with, including rationale for why you believe this to be the case.
    Your analysis should be in the form of a valid JSON object with a top level key called "changes"
    which contains a list of objects in the form:
    "summary": string containing a plain-text version of your analysis
    "breaking": boolean describing whether this represents a change to existing behavior
    "confidence": percentage representing your confidence in this analysis and whether it is breaking or not"""
    user_prompt = """
    Please analyze the following content:
    Content: \"{content}\"
    """
    cleanup_prompt = """
    You are a software engineer.
    You have been tasked with modifying the following content so that it is syntactically correct JSON,
    but not to alter the structure JSON objects which result. Your modifications should be
    limited to ensuring strings are encapsulated with double quotes and other things which
    would otherwise be caught by automated JSON validation tooling. You may add attributes as you
    find necessary, but do not remove any existing attributes.
    Your analysis should be in the form of a valid JSON object containing a list of objects in the form:
    "summary": string containing a plain-text version of your analysis
    "breaking": boolean describing whether this change is breaking for us or not
    "confidence": percentage representing your confidence in this analysis"""
    cleanup_user_prompt = """
    Please proceed with modifications on the following content:
    Content: \"{content}\""""

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

    def summarize(self, content: str):
        log = self.log.getChild("summarize")
        user_prompt = self.user_prompt.format(content=content)
        log.debug("System Prompt:", self.system_prompt)
        log.debug("User Prompt:", user_prompt)
        log.info("Analyzing blog post...")
        analysis_response = self.openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
        structured_response = analysis_response["choices"][0]["message"]["content"]
        try:
            return_value = json.loads(structured_response)
            return return_value
        except json.decoder.JSONDecodeError:
            try:
                log.debug(structured_response)
                cleaned_up_response = self.openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.cleanup_prompt},
                        {
                            "role": "user",
                            "content": self.cleanup_user_prompt.format(
                                content=structured_response
                            ),
                        },
                    ],
                    temperature=0.1,
                )
                log.debug(cleaned_up_response["choices"][0]["message"]["content"])
                return json.loads(
                    format_summary_response(
                        cleaned_up_response["choices"][0]["message"]["content"]
                    )
                )
            except Exception as e:
                log.exception(e)
                raise e
        except Exception as e:
            log.exception(e)
            raise e
