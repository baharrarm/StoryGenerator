from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.auth import LoginIn, UserCreate, Token
from app.security import cognito
from app.controllers.auth_controller import upsert_local_user
from pydantic import BaseModel, EmailStr, Field
from botocore.exceptions import ClientError


router = APIRouter(prefix="/v1/auth", tags=["auth"])

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        cognito.sign_up(user.username, user.password, user.email)
    except ClientError as e:
        raise HTTPException(status_code=400, detail=e.response["Error"]["Message"])
    upsert_local_user(db, username=user.username, email=user.email)
    return {"message": "Check your email for the confirmation code."}

@router.post("/confirm")
def confirm(username: str, code: str):
    try:
        cognito.confirm_sign_up(username, code)
    except ClientError as e:
        raise HTTPException(status_code=400, detail=e.response["Error"]["Message"])
    return {"message": "Email confirmed."}

@router.post("/login", response_model=Token)
def login(body: LoginIn, db: Session = Depends(get_db)):
    try:
        auth = cognito.login(body.username, body.password)
    except ClientError as e:
        raise HTTPException(status_code=400, detail=e.response["Error"]["Message"])
    upsert_local_user(db, username=body.username, email=None)
    return {"access_token": auth["IdToken"], "token_type": "bearer"}

@router.post("/email/change")
def email_change(access_token: str, new_email: EmailStr):
    cognito.update_email(access_token, new_email)
    return {"message": "Verification code sent to new email."}

@router.post("/email/confirm")
def email_confirm(access_token: str, code: str):
    cognito.confirm_email(access_token, code)
    return {"message": "Email verified."}

class PasswordChangeIn(BaseModel):
    access_token: str
    old_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)

@router.post("/password/change")
def password_change(body: PasswordChangeIn):
    cognito.change_password(body.access_token, body.old_password, body.new_password)
    return {"message": "Password changed."}
