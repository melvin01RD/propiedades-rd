from pydantic import BaseModel, EmailStr, field_validator
from src.persistence.models.user import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("role")
    @classmethod
    def role_must_not_be_admin(cls, v: UserRole) -> UserRole:
        if v == UserRole.admin:
            raise ValueError("No puedes registrarte como administrador")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
