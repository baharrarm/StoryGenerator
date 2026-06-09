from typing import Optional
import time
from typing import Tuple
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
# from jose import jwk

from app.db import SessionLocal
from app.models.user import User


AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
COGNITO_ISSUER = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
# cache JWKS once
# _JWKS = httpx.get(f"{COGNITO_ISSUER}/.well-known/jwks.json", timeout=5).json()
_JWKS_CACHE: Tuple[dict, float] | None = None  # (jwks_json, fetched_at)
_JWKS_TTL_SEC = 3600

def _get_jwks() -> dict:
    global _JWKS_CACHE
    now = time.time()
    if _JWKS_CACHE and (now - _JWKS_CACHE[1] < _JWKS_TTL_SEC):
        return _JWKS_CACHE[0]
    # fetch fresh (and tolerate brief network issues by reusing stale if present)
    try:
        jwks = httpx.get(f"{COGNITO_ISSUER}/.well-known/jwks.json", timeout=5).json()
        _JWKS_CACHE = (jwks, now)
        return jwks
    except Exception:
        if _JWKS_CACHE:
            return _JWKS_CACHE[0]
        raise


reuse_guard = HTTPBearer(auto_error=False)

# def _decode_username(token: str) -> Optional[str]:
def _decode_claims(token: str) -> Optional[dict]:
    try:
        hdr = jwt.get_unverified_header(token)
        kid = hdr.get("kid")
        # key = next((k for k in _JWKS["keys"] if k["kid"] == kid), None)
        # if not key:
        #     return None
        # claims = jwt.decode(
        #     token,
        #     key,
        #     algorithms=["RS256"],
        #     audience=COGNITO_CLIENT_ID,
        #     issuer=COGNITO_ISSUER,
        # )
        jwks = _get_jwks()
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            # key likely rotated — refresh once and retry
            _JWKS_CACHE = None
            jwks = _get_jwks()
            key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
            if not key:
                return None
        claims = jwt.decode(token, key, algorithms=["RS256"],
                            audience=COGNITO_CLIENT_ID, issuer=COGNITO_ISSUER)
        # return claims.get("cognito:username") or claims.get("email")
        return claims
    except Exception:
        return None

def get_current_user_optional(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(reuse_guard),
) -> Optional[User]:
    if not creds:
        return None
    # username = _decode_username(creds.credentials)
    # if not username:
    #     return None

    claims = _decode_claims(creds.credentials)
    if not claims:
         return None
    username = claims.get("cognito:username") or claims.get("email")

    # short-lived DB session
    with SessionLocal() as s:
        # return s.query(User).filter_by(username=username).first()
        u = s.query(User).filter_by(username=username).first()
        if u:
            setattr(u, "groups", claims.get("cognito:groups", []))
        return u


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(reuse_guard),
) -> User:
    if not creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    # username = _decode_username(creds.credentials)
    # if not username:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid token",
    #     )
    claims = _decode_claims(creds.credentials)
    if not claims:
         raise HTTPException(status_code=401, detail="Invalid token")
    username = claims.get("cognito:username") or claims.get("email")

    with SessionLocal() as s:
        user = s.query(User).filter_by(username=username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        setattr(user, "groups", claims.get("cognito:groups", []))
        return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    # if getattr(user, "role", "") != "admin":
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    groups = getattr(user, "groups", []) or []
    if getattr(user, "role", "") != "admin" and "Admin" not in groups:
        raise HTTPException(status_code=403, detail="Admin only")
    return user
