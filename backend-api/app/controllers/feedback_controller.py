from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from app.models.feedback import StoryFeedback
from app.models.story_metadata import StoryMetadata
from app.models.user import User

def _can_access_story(user: User, story: StoryMetadata) -> bool:
#     return user.role == "admin" or story.owner_id == user.id
    is_admin = user.role == "admin" or "Admin" in (getattr(user, "groups", []) or [])
    return is_admin or story.owner_id == user.id

def create_feedback(db: Session, user: User, story_id: int, rating: int, notes: str | None):
    story = db.get(StoryMetadata, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    if not _can_access_story(user, story):
        raise HTTPException(status_code=403, detail="Not allowed to leave feedback on this story")

    fb = StoryFeedback(story_id=story_id, user_id=user.id, rating=rating, notes=notes)
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb

def list_feedback_for_story(db: Session, user: User, story_id: int):
    story = db.get(StoryMetadata, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    if not _can_access_story(user, story):
        raise HTTPException(status_code=403, detail="Not allowed to view feedback for this story")

    q = (
        select(StoryFeedback)
        .where(
            StoryFeedback.story_id == story_id,
            StoryFeedback.user_id == user.id,
        )
        .order_by(StoryFeedback.created_at.desc())
    )
    return db.execute(q).scalars().all()

def get_user_avg_rating(db: Session, user_id: int) -> float | None:
    avg = db.execute(
        select(func.avg(StoryFeedback.rating))
        .select_from(StoryFeedback)
        .join(StoryMetadata, StoryFeedback.story_id == StoryMetadata.id)
        .where(StoryMetadata.owner_id == user_id)
    ).scalar()
    return float(avg) if avg is not None else None
