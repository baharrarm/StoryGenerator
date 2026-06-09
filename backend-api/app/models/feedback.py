from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, CheckConstraint, func
from sqlalchemy.orm import relationship
from app.db import Base

class StoryFeedback(Base):
    __tablename__ = "story_feedback"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)   # 1..5
    notes  = Column(Text, nullable=True) # feedback text
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    story = relationship("StoryMetadata", backref="feedback")
    user  = relationship("User", backref="given_feedback")

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_feedback_rating_range"),
    )
