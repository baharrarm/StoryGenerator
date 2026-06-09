from typing import Optional
import time
from typing import Tuple
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

from app.db import SessionLocal
from app.models.user import User

AUTH_PROVIDER = os.getenv("AUTH_PROVIDER", "local")  # was: cognito (Cognito user pool)

# Cognito settings (only used when AUTH_PROVIDER=cognito)
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
COGNITO_ISSUER = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
_JWKS_CACHE: Tuple[dict, float] | None = None
_JWKS_TTL_SEC = 3600

def _get_jwks() -> dict:
    global _JWKS_CACHE
    now = time.time()
    if _JWKS_CACHE and (now - _JWKS_CACHE[1] < _JWKS_TTL_SEC):
        return _JWKS_CACHE[0]
    try:
        jwks = httpx.get(f"{COGNITO_ISSUER}/.well-known/jwks.json", timeout=5).json()
        _JWKS_CACHE = (jwks, now)
        return jwks
    except Exception:
        if _JWKS_CACHE:
            return _JWKS_CACHE[0]
        raise


reuse_guard = HTTPBearer(auto_error=False)

def _decode_claims(token: str) -> Optional[dict]:
    if AUTH_PROVIDER == "local":
        # Local mode: HS256 JWT signed with JWT_SECRET (issued by /auth/login)
        # Cognito mode used RS256 verified against pool JWKS
        try:
            from app.utils.security import SECRET_KEY, ALGORITHM
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except Exception:
            return None

    # Cognito: verify RS256 token against pool JWKS
    try:
        hdr = jwt.get_unverified_header(token)
        kid = hdr.get("kid")
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
        return claims
    except Exception:
        return None


def _user_from_claims(claims: dict, s) -> Optional[User]:
    if AUTH_PROVIDER == "local":
        # Local JWT: sub = user.id (string)
        user_id = claims.get("sub")
        u = s.query(User).filter_by(id=int(user_id)).first()
        if u:
            setattr(u, "groups", ["Admin"] if u.role == "admin" else [])
        return u
    # Cognito JWT: cognito:username or email
    username = claims.get("cognito:username") or claims.get("email")
    u = s.query(User).filter_by(username=username).first()
    if u:
        setattr(u, "groups", claims.get("cognito:groups", []))
    return u


def get_current_user_optional(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(reuse_guard),
) -> Optional[User]:
    if not creds:
        return None
    claims = _decode_claims(creds.credentials)
    if not claims:
        return None
    with SessionLocal() as s:
        return _user_from_claims(claims, s)


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(reuse_guard),
) -> User:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    claims = _decode_claims(creds.credentials)
    if not claims:
        raise HTTPException(status_code=401, detail="Invalid token")
    with SessionLocal() as s:
        user = _user_from_claims(claims, s)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    groups = getattr(user, "groups", []) or []
    if getattr(user, "role", "") != "admin" and "Admin" not in groups:
        raise HTTPException(status_code=403, detail="Admin only")
    return user
