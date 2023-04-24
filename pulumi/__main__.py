"""An AWS Python Pulumi program"""

from pulumi_aws_native import s3

import pulumi

bucket = s3.Bucket("aws-blog-rss-feed")

# Export the name of the bucket
pulumi.export("s3_bucket_name", bucket.bucket_name)
