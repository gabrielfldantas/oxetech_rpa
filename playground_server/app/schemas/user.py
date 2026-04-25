from typing import Literal

from pydantic import BaseModel, EmailStr, Field

Role = Literal["admin", "manager", "seller", "viewer"]


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    role: Role = "viewer"


class UserUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    role: Role
    active: bool


class UserPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    role: Role | None = None
    active: bool | None = None


class UserPublicResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    active: bool

    model_config = {"from_attributes": True}


class UserResponse(UserPublicResponse):
    api_key: str
