from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.item import ItemCreate, ItemPatch, ItemResponse, ItemUpdate
from app.services import item_service

router = APIRouter(prefix="/items", tags=["Items"])

ReadAccess = Depends(require_role("admin", "manager", "seller", "viewer"))
WriteAccess = Depends(require_role("admin", "manager"))


@router.get("/", response_model=list[ItemResponse])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: User = ReadAccess,
):
    return item_service.list_items(db, skip, limit)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    _current_user: User = ReadAccess,
):
    return item_service.get_item(db, item_id)


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    _current_user: User = WriteAccess,
):
    return item_service.create_item(db, data)


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    data: ItemUpdate,
    db: Session = Depends(get_db),
    _current_user: User = WriteAccess,
):
    return item_service.update_item(db, item_id, data)


@router.patch("/{item_id}", response_model=ItemResponse)
def patch_item(
    item_id: int,
    data: ItemPatch,
    db: Session = Depends(get_db),
    _current_user: User = WriteAccess,
):
    return item_service.patch_item(db, item_id, data)


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _current_user: User = WriteAccess,
):
    item_service.delete_item(db, item_id)
