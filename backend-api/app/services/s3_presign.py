import os, boto3
from botocore.config import Config

S3_BUCKET = os.getenv("STORY_BUCKET")
REGION = os.getenv("AWS_REGION", "ap-southeast-2")

cfg = Config(retries={"max_attempts": 5, "mode": "standard"}, connect_timeout=5, read_timeout=10)
s3 = boto3.client("s3", region_name=REGION, config=cfg)
if os.getenv("APP_ENV") == "prod" and not S3_BUCKET:
    raise RuntimeError("STORY_BUCKET must be set in production")

def presign_get(key: str, expires: int = 900) -> str:
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=expires,
        HttpMethod="GET",
    )
