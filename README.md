# AWS RSS Feed Bot

## Overview

This is a CLI tool which leverages current state-of-the-art AI tooling to summarize AWS blog posts as relates to automated tooling vendors which integrate with AWS services. The goal is to provide context at-a-glance which will inform whether the announcements being made by AWS will result in downstream breaking changes for AWS partners based on the content of the announcements themselves. We provide a simple CLI to interact with this tool which will be expanded over time, with more configuration options to come.

## Usage
Currently, the interface to this tool is relatively straightforward. Fill out any missing credentials (minimally, set `OPENAI_API_KEY` in your environment), and run:
```shell
poetry install
poetry run cli
```

Flags can be added as well:
```shell
Usage: cli [OPTIONS]

Options:
  -c, --checkpoint
  -v, --verbosity [DEBUG|INFO|WARNING]
  --help                          Show this message and exit.
```

## Example Output

For a sample blog post [like this one](https://aws.amazon.com/blogs/aws/aws-week-in-review-april-24-2023-amazon-codecatalyst-amazon-s3-on-snowball-edge-and-more/), users can expect output similar to this:

```json
{
    "announcements": [
        {
            "summary": "Amazon CodeCatalyst is now generally available, providing a unified software development and delivery service.",
            "breaking": False,
            "confidence": 95,
        },
        {
            "summary": "Amazon S3 is now available on Snowball Edge devices, allowing for an expanded set of S3 APIs and easier application deployment.",
            "breaking": False,
            "confidence": 95,
        },
        {
            "summary": "Version 1.0.0 of AWS Amplify Flutter is released, enabling cross-platform app development for iOS, Android, Web, and desktop.",
            "breaking": False,
            "confidence": 95,
        },
        {
            "summary": "Amazon Redshift updates include the MERGE SQL command, dynamic data masking, and centralized access control for data sharing with AWS Lake Formation.",
            "breaking": False,
            "confidence": 95,
        },
        {
            "summary": "AWS Amplify now supports Push Notifications for Android, Swift, React Native, and Flutter apps.",
            "breaking": False,
            "confidence": 95,
        },
        {
            "summary": "Several AWS services have been expanded to additional regions and locations.",
            "breaking": False,
            "confidence": 95,
        },
    ]
}
```