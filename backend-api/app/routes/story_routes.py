from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.story import StoryRequest, StoryResponse, StoryDetail
from app.controllers.story_controller import generate_and_optionally_save, get_story_detail, delete_story
from app.utils.deps import get_current_user_optional, get_current_user
from app.schemas.feedback import FeedbackIn, FeedbackOut
from app.controllers.feedback_controller import create_feedback, list_feedback_for_story
from typing import List
from app.services.s3_presign import presign_get
from app.models.story_metadata import StoryMetadata
from app.utils.deps import get_current_user
from fastapi import HTTPException, status

router = APIRouter(prefix="/v1/stories", tags=["stories"])

@router.post("/generate", response_model=StoryResponse)
def generate_story_ep(
    body: StoryRequest,
    current_user = Depends(get_current_user_optional),
):
    result = generate_and_optionally_save(
        prompt=body.prompt,
        genre=body.genre,
        style=body.style,
        length=body.length,
        current_user=current_user,
        use_random_character=body.use_random_character,
    )
    return result


@router.get("/{story_id}", response_model=StoryDetail)
def get_story(
    story_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),   # require auth
):
    return get_story_detail(db, story_id, current_user)


@router.delete("/{story_id}")
def delete_story_ep(
    story_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return delete_story(db=db, story_id=story_id, requester=current_user)


@router.post("/{story_id}/feedback", response_model=FeedbackOut)
def add_feedback(
    story_id: int,
    body: FeedbackIn,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return create_feedback(db, current_user, story_id, body.rating, body.notes)


@router.get("/{story_id}/feedback", response_model=List[FeedbackOut])
def get_feedback(
    story_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return list_feedback_for_story(db, current_user, story_id)

@router.get("/{story_id}/download-url")
def story_download_url(
    story_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    meta = db.get(StoryMetadata, story_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Story not found")
    is_owner = meta.owner_id == current_user.id
    if not (is_owner):
        raise HTTPException(status_code=403, detail="Not allowed")
    return {"url": presign_get(meta.file_path)}
