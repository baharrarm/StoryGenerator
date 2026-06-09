from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.auth import UserOut
from app.schemas.story import StoryMetaOut
from app.utils.deps import require_admin
from app.controllers.admin_controller import list_users, list_all_stories, delete_user_cascade

router = APIRouter(prefix="/v1/admin", tags=["admin"])

@router.get("/users", response_model=List[UserOut])
def admin_list_users(
    _admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return list_users(db)

@router.get("/stories", response_model=List[StoryMetaOut])
def admin_list_stories(
    genre: str | None = None,
    style: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    limit: int = 20,
    offset: int = 0,
    _admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return list_all_stories(db, genre, style, sort_by, order, limit, offset)

@router.delete("/users/{user_id}")
def admin_delete_user(
    user_id: int,
    _admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return delete_user_cascade(db, user_id)

