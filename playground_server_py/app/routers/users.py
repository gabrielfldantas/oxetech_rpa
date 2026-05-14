from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserPatch,
    UserPublicResponse,
    UserResponse,
    UserUpdate,
)
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])

AdminOnly = Depends(require_role("admin"))


@router.get("/", response_model=list[UserPublicResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: User = AdminOnly,
):
    return user_service.list_users(db, skip, limit)


@router.get("/{user_id}", response_model=UserPublicResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user: User = AdminOnly,
):
    return user_service.get_user(db, user_id)


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _current_user: User = AdminOnly,
):
    return user_service.create_user(db, data)


@router.put("/{user_id}", response_model=UserPublicResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _current_user: User = AdminOnly,
):
    return user_service.update_user(db, user_id, data)


@router.patch("/{user_id}", response_model=UserPublicResponse)
def patch_user(
    user_id: int,
    data: UserPatch,
    db: Session = Depends(get_db),
    _current_user: User = AdminOnly,
):
    return user_service.patch_user(db, user_id, data)


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user: User = AdminOnly,
):
    user_service.delete_user(db, user_id)
