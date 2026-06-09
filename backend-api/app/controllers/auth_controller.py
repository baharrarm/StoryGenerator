from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.utils.security import hash_password, verify_password, create_access_token

# def register_user(db: Session, username: str, password: str):
#     existing = db.query(User).filter(User.username == username).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Username already exists")

#     user = User(username=username, hashed_password=hash_password(password))
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user

# def login_user(db: Session, username: str, password: str):
#     user = db.query(User).filter(User.username == username).first()
#     if not user or not verify_password(password, user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     token = create_access_token({"sub": str(user.id), "role": user.role})
#     return token, user

def upsert_local_user(db: Session, username: str, email: str | None):
    u = db.query(User).filter(User.username == username).first()
    if not u:
        u = User(username=username, email=email, hashed_password=None)
        db.add(u)
    else:
        if email and not u.email:
            u.email = email
    db.commit()
    db.refresh(u)
    return u

