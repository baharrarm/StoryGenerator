from pydantic import BaseModel, Field
from datetime import datetime

class FeedbackIn(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    notes: str | None = None

class FeedbackOut(BaseModel):
    id: int
    story_id: int
    user_id: int
    rating: int
    notes: str | None
    created_at: datetime
    class Config:
        from_attributes = True
