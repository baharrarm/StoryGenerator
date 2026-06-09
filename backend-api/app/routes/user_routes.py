from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.user import MeOut, UpdateMe, PreferencesIn, PreferencesOut
from app.schemas.story import StoryMetaOut
from app.utils.deps import get_current_user
from app.controllers.user_controller import get_me, update_me, upsert_my_preferences, get_my_preferences, delete_me_cascade
from app.controllers.story_controller import list_my_stories

router = APIRouter(prefix="/v1/users", tags=["users"])

# Get profile details
@router.get("/me", response_model=MeOut)
def me(current_user = Depends(get_current_user)):
    return get_me(current_user)

@router.patch("/me", response_model=MeOut)
def update_profile(
    body: UpdateMe,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # updated = update_me(db, current_user, body.username, body.password)

    # Username/password are managed by Cognito
    if body.username is not None or body.password is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Change username/password via Cognito.")
    updated = current_user
    return updated

@router.get("/me/preferences", response_model=PreferencesOut | None)
def get_prefs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    row = get_my_preferences(db, current_user)
    if not row:
        return None
    return PreferencesOut(
        default_genre=row.default_genre,
        default_style=row.default_style,
        default_length=row.default_length,
    )

@router.put("/me/preferences", response_model=PreferencesOut | None)
def put_prefs(
    body: PreferencesIn,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    row = upsert_my_preferences(db, current_user, body.dict())
    if not row:
        return None
    return PreferencesOut(
        default_genre=row.default_genre,
        default_style=row.default_style,
        default_length=row.default_length,
    )

@router.delete("/me")
def delete_my_account(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return delete_me_cascade(db, current_user)

# Get a user's stories
@router.get("/my-stories", response_model=List[StoryMetaOut])
def my_stories(
    genre: str | None = None,
    style: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return list_my_stories(db, current_user, genre, style, sort_by, order, limit, offset)

