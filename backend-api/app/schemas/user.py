from pydantic import BaseModel, Field, EmailStr

class MeOut(BaseModel):
    id: int
    username: str
    email: EmailStr | None = None
    role: str
    groups: list[str] | None = None
    class Config:
        from_attributes = True

class UpdateMe(BaseModel):
    username: str | None = None
    password: str | None = Field(default=None, min_length=4)  # email managed by Cognito

class PreferencesIn(BaseModel):
    default_genre: str | None = None
    default_style: str | None = None
    default_length: int | None = Field(default=None, ge=50, le=1200)

class PreferencesOut(BaseModel):
    default_genre: str | None = None
    default_style: str | None = None
    default_length: int | None = None