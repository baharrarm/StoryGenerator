from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from fastapi import HTTPException, status
from app.models.user import User
from app.models.story_metadata import StoryMetadata
from app.storage.story_store import delete_story_file
from app.security.cognito import admin_delete_cognito_user

def list_users(db: Session):
    rows = db.execute(select(User).order_by(User.id.asc())).scalars().all()
    return rows

def list_all_stories(
    db: Session,
    genre: str | None = None,
    style: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    limit: int = 20,
    offset: int = 0,
):
    query = select(StoryMetadata)

    # Filtering
    if genre:
        query = query.where(StoryMetadata.genre == genre)
    if style:
        # only filter if column exists
        col = getattr(StoryMetadata, "style", None)
        if col is not None:
            query = query.where(col == style)

    # Sorting
    sort_col = getattr(StoryMetadata, sort_by, StoryMetadata.created_at)
    if order.lower() == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    # Pagination
    query = query.limit(limit).offset(offset)

    return db.execute(query).scalars().all()


def delete_user_cascade(db: Session, user_id: int):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # remove from Cognito first
    try:
        if user.username:
            admin_delete_cognito_user(user.username)
    except Exception:
        pass 

    # delete that user's story files + rows
    stories = db.execute(
        select(StoryMetadata).where(StoryMetadata.owner_id == user_id)
    ).scalars().all()
    for s in stories:
        # delete_story_file(s.file_path)
        key = getattr(s, "s3_key", None) or getattr(s, "file_path", None)
        if key:
            delete_story_file(key)
        db.delete(s)

    # delete the user
    db.delete(user)
    db.commit()
    return {"deleted_user_id": user_id, "deleted_story_count": len(stories)}
