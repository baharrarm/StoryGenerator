# app/workers/sqs_worker.py
import os, json, time, threading, logging
import boto3
from botocore.config import Config

from app.services.story_generator import generate_story
from app.storage.story_store import write_story_text
from app.models.story_metadata import StoryMetadata
from app.db import SessionLocal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

_thread = None

SQS_URL   = os.getenv("SQS_QUEUE_URL")
DLQ_URL   = os.getenv("SQS_DLQ_URL")
REGION    = os.getenv("AWS_REGION", "ap-southeast-2")
MODE      = os.getenv("WORKER_MODE", "main").lower()  # "main" or "dlq"
INITIAL_VIS_TIMEOUT = int(os.getenv("SQS_VISIBILITY_TIMEOUT", "90"))

aws_cfg = Config(retries={"max_attempts": 5, "mode": "standard"})
sqs = boto3.client("sqs", region_name=REGION, config=aws_cfg)

s3 = boto3.client("s3", region_name=REGION, config=aws_cfg)
DLQ_ARCHIVE_BUCKET = os.getenv("DLQ_ARCHIVE_BUCKET")


def handle_message(msg_body: dict) -> bool:
    try:
        prompt = msg_body["prompt"]
        genre = msg_body.get("genre")
        style = msg_body.get("style")
        length = msg_body.get("length", 200)
        temperature = msg_body.get("temperature", 0.9)
        top_p = msg_body.get("top_p", 0.92)
        user_id = msg_body.get("user_id")
        job_id = msg_body.get("job_id")

        text = generate_story(
            prompt, genre, style, length,
            temperature=temperature, top_p=top_p
        )

        if not user_id or not SessionLocal:
            logging.info("No user_id or DB session; generated but not persisted.")
            return True

        key, _sid = write_story_text(user_id, text)
        logging.info("S3 saved: %s", key)

        db = SessionLocal()
        try:
            if job_id:
                existing = db.query(StoryMetadata).filter_by(job_id=job_id).first()
                if existing:
                    logging.info("Job %s already processed", job_id)
                    return True
            meta = StoryMetadata(
                title=(prompt[:60] or "Story").strip(),
                genre=genre or "",
                owner_id=user_id,
                job_id=job_id,
                file_path=key,
            )
            db.add(meta); db.commit()
            logging.info("DB insert ok for user_id=%s", user_id)
            return True
        except Exception as ex:
            logging.error("DB insert failed: %s", ex); db.rollback()
            return False
        finally:
            db.close()

    except Exception as ex:
        logging.exception("Unhandled error in handle_message: %s", ex)
        return False


def poll_loop():
    if not SQS_URL:
        logging.error("SQS_QUEUE_URL not set; worker not started")
        return

    while True:
        resp = sqs.receive_message(
            QueueUrl=SQS_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,                 # long polling
            VisibilityTimeout=INITIAL_VIS_TIMEOUT,
            AttributeNames=["ApproximateReceiveCount"],
        )
        msgs = resp.get("Messages", [])
        if not msgs:
            continue

        m = msgs[0]
        receipt = m["ReceiptHandle"]
        body_text = m["Body"]
        try:
            body = json.loads(body_text)
        except Exception:
            body = {"raw": body_text}

        recv_count = int(m.get("Attributes", {}).get("ApproximateReceiveCount", "1"))
        logging.info("Got message (ApproxReceiveCount=%d): %s", recv_count, body_text[:200])

        # Heartbeat to keep visibility alive if processing can be long
        stop_hb = False
        def _heartbeat():
            while not stop_hb:
                time.sleep(max(1, INITIAL_VIS_TIMEOUT // 3))
                try:
                    sqs.change_message_visibility(
                        QueueUrl=SQS_URL, ReceiptHandle=receipt,
                        VisibilityTimeout=INITIAL_VIS_TIMEOUT
                    )
                except Exception as he:
                    logging.debug("Heartbeat error: %s", he)

        hb = threading.Thread(target=_heartbeat, daemon=True)
        hb.start()

        ok = False
        try:
            ok = handle_message(body)
        finally:
            stop_hb = True

        if ok:
            try:
                sqs.delete_message(QueueUrl=SQS_URL, ReceiptHandle=receipt)
                logging.info("Processed & deleted message.")
            except Exception as de:
                logging.error("Delete failed: %s", de)
        else:
            logging.warning("Processing failed (attempt %d). Leaving for retry/DLQ.", recv_count)

        time.sleep(0.5)


def dlq_drain_loop():
    if not DLQ_URL:
        logging.error("SQS_DLQ_URL not set; DLQ drainer not started")
        return
    logging.info("DLQ drainer started")
    while True:
        resp = sqs.receive_message(
            QueueUrl=DLQ_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20
        )
        for m in resp.get("Messages", []):
            body = m["Body"]
            logging.error("DLQ message: %s", body[:500])

            # Archive to S3 for debugging / offline reprocessing
            if DLQ_ARCHIVE_BUCKET:
                try:
                    key = f"dlq/{int(time.time())}-{m['MessageId']}.json"
                    s3.put_object(
                        Bucket=DLQ_ARCHIVE_BUCKET,
                        Key=key,
                        Body=body.encode("utf-8"),
                    )
                    logging.info("DLQ message archived to s3://%s/%s", DLQ_ARCHIVE_BUCKET, key)
                except Exception as ex:
                    logging.error("Failed to archive DLQ message: %s", ex)

            # Remove from DLQ so it doesn’t loop forever
            try:
                sqs.delete_message(QueueUrl=DLQ_URL, ReceiptHandle=m["ReceiptHandle"])
            except Exception as de:
                logging.error("DLQ delete failed: %s", de)

        time.sleep(0.5)


def start_worker_thread():
    """Start the appropriate loop in a background thread (for FastAPI apps)."""
    global _thread
    if _thread and _thread.is_alive():
        return
    target = dlq_drain_loop if MODE == "dlq" else poll_loop
    logging.info("Starting background thread in %s mode…", MODE)
    _thread = threading.Thread(target=target, daemon=True)
    _thread.start()

def is_worker_alive():
    return _thread.is_alive() if _thread else False


if __name__ == "__main__":
    # If you ever run this module directly: python -m app.workers.sqs_worker
    if MODE == "dlq":
        dlq_drain_loop()
    else:
        poll_loop()
