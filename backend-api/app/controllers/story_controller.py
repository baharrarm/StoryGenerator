from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from app.controllers.feedback_controller import get_user_avg_rating

from app.models.story_metadata import StoryMetadata
from app.models.user import User

import os, httpx, json
from app.services.external_char import get_random_character
from app.storage.story_store import write_story_text, read_story_text, delete_story_file
from app.db import SessionLocal
import boto3
import uuid

GENERATOR_URL = os.getenv("GENERATOR_URL", "http://localhost:8001")
_SQS_URL = os.getenv("SQS_QUEUE_URL")
_sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION", "ap-southeast-2"))

def _decode_params_from_avg(avg: float | None) -> tuple[float, float]:
    # Baseline if no feedback yet
    if avg is None:
        return 0.9, 0.92
    # Map avg  [1,5] to temperature [1.15, 0.85]
    # lower avg = more creativity
    t = 1.15 - (max(1.0, min(5.0, avg)) - 1.0) * (0.30 / 4.0)  # 1.15..0.85
    p = 0.88 + (5.0 - max(1.0, min(5.0, avg))) * (0.10 / 4.0)  # ~0.88..0.98
    return round(t, 2), round(p, 2)

def generate_and_optionally_save(
    prompt: str,
    genre: str | None,
    style: str | None,
    length: int,
    current_user: User | None,
    use_random_character: bool = False,
):
    
    if use_random_character:
        try:
            ch = get_random_character()
            prompt = f"{prompt}\nMain character: {ch['name']} ({ch['traits']})."
        except Exception:
            # if external API down continue with original prompt.
            pass
        
    avg = None
    if current_user is not None:
        with SessionLocal() as s:
            avg = get_user_avg_rating(s, current_user.id)

    temperature, top_p = _decode_params_from_avg(avg)

    if not _SQS_URL:
        raise HTTPException(status_code=500, detail="SQS queue not configured")

    job_id = str(uuid.uuid4())

    body = {
        "job_id": job_id,
        "prompt": prompt,
        "genre": genre,
        "style": style,
        "length": length,
        "temperature": temperature,
        "top_p": top_p,
        "user_id": current_user.id if current_user else None,
    }

    _sqs.send_message(
        QueueUrl=_SQS_URL,
        MessageBody=json.dumps(body),
    )
    
    return {
        "status": "queued",
        "saved": current_user is not None,
        "job_id": job_id,
        "story_id": None,
    }


def list_my_stories(
    db: Session,
    user: User,
    genre: str | None = None,
    style: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    limit: int = 20,
    offset: int = 0,
):
    query = select(StoryMetadata).where(StoryMetadata.owner_id == user.id)

    # Filtering
    if genre:
        query = query.where(StoryMetadata.genre == genre)
    if style and hasattr(StoryMetadata, "style"):
        query = query.where(getattr(StoryMetadata, "style") == style)

    # Sorting
    sort_col = getattr(StoryMetadata, sort_by, StoryMetadata.created_at)
    if order.lower() == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    # Pagination
    query = query.limit(limit).offset(offset)

    return db.execute(query).scalars().all()

def get_story_detail(db: Session, story_id: int, current_user: User):
    meta = db.get(StoryMetadata, story_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Story not found")

    is_owner = current_user and meta.owner_id == current_user.id
    # is_admin = current_user and getattr(current_user, "role", "") == "admin"
    is_admin = current_user and (
        getattr(current_user, "role", "") == "admin"
        or "Admin" in (getattr(current_user, "groups", []) or [])
    )
    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="Not allowed to view this story")

    text = read_story_text(meta.file_path) if meta.file_path else ""
    if text == "":
        raise HTTPException(status_code=410, detail="Story file not available")

    return {
        "id": meta.id,
        "title": meta.title,
        "genre": meta.genre,
        "owner_id": meta.owner_id,
        "created_at": meta.created_at,
        "content": text,
    }

def delete_story(db: Session, story_id: int, requester: User):
    story = db.get(StoryMetadata, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    is_owner = requester.id == story.owner_id
    # is_admin = requester.role == "admin"
    is_admin = requester.role == "admin" or "Admin" in (getattr(requester, "groups", []) or [])
    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="Not allowed")

    # remove file then DB row
    delete_story_file(story.file_path)
    db.delete(story)
    db.commit()
    return {"deleted": True, "id": story_id}

