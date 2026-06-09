from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class StoryRequest(BaseModel):
    prompt: str = Field(..., min_length=3)
    genre: str | None = None
    style: str | None = None
    length: int = Field(200, ge=50, le=1200)
    use_random_character: bool = False

class StoryResponse(BaseModel):
    story: Optional[str] = None
    saved: bool = False
    story_id: Optional[int] = None
    storage_key: Optional[str] = None
    status: Optional[Literal["queued", "ok", "completed"]] = None  # "completed" added for local HTTP path
    job_id: Optional[str] = None

class StoryMetaOut(BaseModel):
    id: int
    title: str
    genre: str | None = None
    created_at: datetime
    class Config:
        from_attributes = True

class StoryDetail(BaseModel):
    id: int
    title: str | None = None
    genre: str | None = None
    owner_id: int | None = None
    created_at: datetime
    content: str