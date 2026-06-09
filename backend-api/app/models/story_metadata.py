from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base

class StoryMetadata(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    genre = Column(String, nullable=True)
    job_id = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Link to user
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")

    # Path to unstructured story file
    file_path = Column(Text, nullable=False)
