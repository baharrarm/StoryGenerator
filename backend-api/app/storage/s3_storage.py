import os, boto3
from botocore.exceptions import ClientError
from botocore.config import Config

BUCKET = os.getenv("STORY_BUCKET")
REGION = os.getenv("AWS_REGION", "ap-southeast-2")

_cfg = Config(
    retries={"max_attempts": 5, "mode": "standard"},
    connect_timeout=5,
    read_timeout=10,
)

s3 = boto3.client("s3", region_name=REGION, config=_cfg)
if os.getenv("APP_ENV") == "prod" and not BUCKET:
    raise RuntimeError("STORY_BUCKET must be set in production")

def save_story(key: str, content: str):
    s3.put_object(Bucket=BUCKET, Key=key, Body=content.encode("utf-8"),
                  ContentType="text/plain; charset=utf-8")

def load_story(key: str) -> str:
    obj = s3.get_object(Bucket=BUCKET, Key=key)
    return obj["Body"].read().decode("utf-8")

def delete_story(key: str):
    s3.delete_object(Bucket=BUCKET, Key=key)

def presign_get(key, expires=900):
    return s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET,"Key": key}, ExpiresIn=expires, HttpMethod="GET")

