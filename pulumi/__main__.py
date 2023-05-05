"""An AWS Python Pulumi program"""

import json
import os

import boto3
import pulumi_aws as aws
import pulumi_aws_native as aws_native
import pulumi_docker as docker

import pulumi


def parse_tag(tag):
    try:
        return int(tag)
    except ValueError:
        return -1


bucket = aws_native.s3.Bucket("aws-blog-rss-feed")

docker_environment = {
    "AWS_RSS_URL": os.getenv("AWS_RSS_URL", "https://aws.amazon.com/blogs/aws/feed/"),
    "AWS_S3_BUCKET_NAME": os.getenv("AWS_S3_BUCKET_NAME", bucket.bucket_name),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN", ""),
    "SLACK_BOT_CHANNEL": os.getenv("SLACK_BOT_CHANNEL", ""),
}

ecr_repo = aws.ecr.Repository(
    "aws-rss-feed-bot-repo",
    name="aws-rss-feed-bot",
    image_scanning_configuration=aws.ecr.RepositoryImageScanningConfigurationArgs(
        scan_on_push=True,
    ),
    image_tag_mutability="MUTABLE",
)

auth_token = aws.ecr.get_authorization_token_output(ecr_repo.registry_id)
ecr = boto3.client("ecr")
images = ecr_repo.name.apply(lambda name: ecr.list_images(repositoryName=name))
tags = images.apply(
    lambda images: [item.get("imageTag", -1) for item in images["imageIds"]]
)
new_tag = tags.apply(lambda tags: max([parse_tag(tag) for tag in tags]) + 1)

docker_image = docker.Image(
    "feed-parser-image",
    opts=pulumi.ResourceOptions(),
    build=docker.DockerBuildArgs(
        context="..",
        dockerfile="../Dockerfile",
        platform="linux/amd64",
        args=docker_environment,
    ),
    image_name=pulumi.Output.all(ecr_repo.repository_url, new_tag).apply(
        lambda args: f"{args[0]}:{args[1]}"
    ),
    registry=docker.RegistryArgs(
        username=auth_token.user_name,
        password=pulumi.Output.secret(auth_token.password),
        server=ecr_repo.repository_url,
    ),
)

lambda_assume_role_policy_document = json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Stmt1683230189332",
                "Action": ["sts:AssumeRole"],
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
            }
        ],
    }
)

lambda_role = aws.iam.Role(
    "aws-rss-feed-bot-role", assume_role_policy=lambda_assume_role_policy_document
)

lambda_policy_document = bucket.arn.apply(
    lambda bucket_arn: json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Stmt1683230189332",
                    "Action": ["s3:ListBucket", "s3:PutObject", "s3:GetObject"],
                    "Effect": "Allow",
                    "Resource": f"{bucket_arn}/*",
                }
            ],
        }
    )
)

lambda_role_policy = aws.iam.RolePolicy(
    "aws-rss-feed-bot-role-policy", policy=lambda_policy_document, role=lambda_role.name
)

base_lambda_execution_policy = aws.iam.get_policy(name="AWSLambdaBasicExecutionRole")
policy_attackment = aws.iam.PolicyAttachment(
    "aws-rss-feed-bot-lambda-policy-attachment",
    roles=[lambda_role.name],
    policy_arn=base_lambda_execution_policy.arn,
)


lambda_function = aws.lambda_.Function(
    "aws-rss-feed-bot-lambda",
    package_type="Image",
    image_uri=docker_image.image_name,
    role=lambda_role.arn,
    name="aws-rss-feed-bot",
    timeout=500,
)

cloudwatch_event = aws.cloudwatch.EventRule(
    "aws-rss-feed-bot-event", schedule_expression="rate(1 hour)"
)
event_target = aws.cloudwatch.EventTarget(
    "aws-rss-feed-bot-event-target", rule=cloudwatch_event.name, arn=lambda_function.arn
)
lambda_permission = aws.lambda_.Permission(
    "aws-rss-feed-bot-lambda-permission",
    action="lambda:InvokeFunction",
    function=lambda_function.name,
    principal="events.amazonaws.com",
    source_arn=cloudwatch_event.arn,
)

# Export the name of the bucket
pulumi.export("image_name", docker_image.image_name)
pulumi.export("lambda_arn", lambda_function.arn)
