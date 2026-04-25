from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.sale import SaleCreate, SalePatch, SaleResponse, SaleUpdate
from app.services import sale_service

router = APIRouter(prefix="/sales", tags=["Sales"])

ReadAccess = Depends(require_role("admin", "manager", "seller", "viewer"))
CreateAccess = Depends(require_role("admin", "manager", "seller"))
WriteAccess = Depends(require_role("admin", "manager"))


@router.get("/", response_model=list[SaleResponse])
def list_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: User = ReadAccess,
):
    return sale_service.list_sales(db, skip, limit)


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    _current_user: User = ReadAccess,
):
    return sale_service.get_sale(db, sale_id)


@router.post("/", response_model=SaleResponse, status_code=201)
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = CreateAccess,
):
    return sale_service.create_sale(db, data, current_user)


@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale(
    sale_id: int,
    data: SaleUpdate,
    db: Session = Depends(get_db),
    _current_user: User = WriteAccess,
):
    return sale_service.update_sale(db, sale_id, data)


@router.patch("/{sale_id}", response_model=SaleResponse)
def patch_sale(
    sale_id: int,
    data: SalePatch,
    db: Session = Depends(get_db),
    _current_user: User = WriteAccess,
):
    return sale_service.patch_sale(db, sale_id, data)


@router.delete("/{sale_id}", status_code=204)
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    _current_user: User = WriteAccess,
):
    sale_service.delete_sale(db, sale_id)
