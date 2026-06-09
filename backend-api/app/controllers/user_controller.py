from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from app.utils.security import hash_password
from app.models.user import User
from app.models.preferences import UserPreferences
from app.models.story_metadata import StoryMetadata
from app.storage.story_store import delete_story_file

def get_me(user: User):
    return user

def update_me(db: Session, user: User, new_username: str | None, new_password: str | None):
    if new_username and new_username != user.username:
        # enforce unique usernames
        exists = db.execute(select(User).where(User.username == new_username)).scalar()
        if exists:
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = new_username
    if new_password:
        user.hashed_password = hash_password(new_password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def upsert_my_preferences(db: Session, user: User, prefs: dict):
    # admins: hide preferences (do nothing, return empty)
    if user.role == "admin":
        return None

    row = db.execute(select(UserPreferences).where(UserPreferences.user_id == user.id)).scalar()
    if not row:
        row = UserPreferences(user_id=user.id)
    row.default_genre = prefs.get("default_genre")
    row.default_style = prefs.get("default_style")
    row.default_length = prefs.get("default_length")
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

def get_my_preferences(db: Session, user: User):
    if user.role == "admin":
        return None
    return db.execute(select(UserPreferences).where(UserPreferences.user_id == user.id)).scalar()

def delete_me_cascade(db: Session, user: User):
    # delete user's stories (files + rows)
    stories = db.execute(
        select(StoryMetadata).where(StoryMetadata.owner_id == user.id)
    ).scalars().all()
    for s in stories:
    #     delete_story_file(s.file_path)
        key = getattr(s, "s3_key", None) or getattr(s, "file_path", None)
        if key:
            delete_story_file(key)
        db.delete(s)

    # delete preferences if exist
    prefs = db.execute(select(UserPreferences).where(UserPreferences.user_id == user.id)).scalar()
    if prefs:
        db.delete(prefs)

    # delete user
    db.delete(user)
    db.commit()
    return {"deleted": True}

