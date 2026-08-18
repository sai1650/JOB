from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: str
    name: str
    email: str
    is_admin: bool
    is_active: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserRead


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    is_admin: bool = False
