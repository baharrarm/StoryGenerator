from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    default_genre = Column(String, nullable=True)
    default_style = Column(String, nullable=True)
    default_length = Column(Integer, nullable=True)

    user = relationship("User")
