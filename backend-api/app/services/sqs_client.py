import os, json, boto3

sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION", "ap-southeast-2"))
QUEUE_URL = os.getenv("SQS_QUEUE_URL")

def enqueue_story(payload: dict):
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(payload),
    )
