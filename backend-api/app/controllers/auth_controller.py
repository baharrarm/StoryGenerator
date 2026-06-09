from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.utils.security import hash_password, verify_password, create_access_token

def register_user(db: Session, username: str, password: str, email: str | None = None):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=username, email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Account created. Proceeding to login."}

def login_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return token, user

def change_local_password(db: Session, user_id: int, old_password: str, new_password: str):
    user = db.query(User).filter_by(id=user_id).first()
    if not user or not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.hashed_password = hash_password(new_password)
    db.commit()
    return {"message": "Password changed."}

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

