from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from app.db import get_db
from app.schemas.auth import LoginIn, UserCreate, Token
from app.security import cognito
from app.controllers.auth_controller import upsert_local_user, register_user, login_user
from pydantic import BaseModel, EmailStr, Field
from botocore.exceptions import ClientError

AUTH_PROVIDER = os.getenv("AUTH_PROVIDER", "local")  # was: cognito (Cognito user pool)

router = APIRouter(prefix="/v1/auth", tags=["auth"])

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if AUTH_PROVIDER == "local":
        return register_user(db, user.username, user.password, user.email)
    # Cognito: sign up then mirror user into local DB
    try:
        cognito.sign_up(user.username, user.password, user.email)
    except ClientError as e:
        raise HTTPException(status_code=400, detail=e.response["Error"]["Message"])
    upsert_local_user(db, username=user.username, email=user.email)
    return {"message": "Check your email for the confirmation code."}

@router.post("/confirm")
def confirm(username: str, code: str):
    if AUTH_PROVIDER == "local":
        # No email verification in local mode; Cognito required this step
        return {"message": "Email confirmed."}
    try:
        cognito.confirm_sign_up(username, code)
    except ClientError as e:
        raise HTTPException(status_code=400, detail=e.response["Error"]["Message"])
    return {"message": "Email confirmed."}

@router.post("/login", response_model=Token)
def login(body: LoginIn, db: Session = Depends(get_db)):
    if AUTH_PROVIDER == "local":
        token, _ = login_user(db, body.username, body.password)
        return {"access_token": token, "token_type": "bearer"}
    # Cognito: authenticate then mirror user into local DB
    try:
        auth = cognito.login(body.username, body.password)
    except ClientError as e:
        raise HTTPException(status_code=400, detail=e.response["Error"]["Message"])
    upsert_local_user(db, username=body.username, email=None)
    return {"access_token": auth["IdToken"], "token_type": "bearer"}

@router.post("/email/change")
def email_change(access_token: str, new_email: EmailStr):
    # Cognito-only; not used in local mode
    cognito.update_email(access_token, new_email)
    return {"message": "Verification code sent to new email."}

@router.post("/email/confirm")
def email_confirm(access_token: str, code: str):
    # Cognito-only; not used in local mode
    cognito.confirm_email(access_token, code)
    return {"message": "Email verified."}

class PasswordChangeIn(BaseModel):
    access_token: str
    old_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)

@router.post("/password/change")
def password_change(body: PasswordChangeIn):
    # Cognito-only; not used in local mode
    cognito.change_password(body.access_token, body.old_password, body.new_password)
    return {"message": "Password changed."}
