from pydantic import BaseModel, Field, EmailStr

class LoginIn(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(min_length=4, max_length=72)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr | None = None
    role: str
    class Config:
        from_attributes = True
