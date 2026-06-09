from sqlalchemy import Column, Integer, String, Boolean
from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    role = Column(String, default="user")  # "user" or "admin"
    is_active = Column(Boolean, default=True)
