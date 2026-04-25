from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.sale import Sale
from app.models.user import User
from app.schemas.sale import SaleCreate, SalePatch, SaleUpdate


def list_sales(db: Session, skip: int = 0, limit: int = 100) -> list[Sale]:
    return db.query(Sale).offset(skip).limit(limit).all()


def get_sale(db: Session, sale_id: int) -> Sale:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venda não encontrada")
    return sale


def create_sale(db: Session, data: SaleCreate, current_user: User) -> Sale:
    item = db.query(Item).filter(Item.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    if item.quantity < data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente. Disponível: {item.quantity}",
        )
    sale = Sale(
        user_id=current_user.id,
        item_id=data.item_id,
        quantity=data.quantity,
        unit_price=item.price,
        total=round(item.price * data.quantity, 2),
    )
    item.quantity -= data.quantity
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def update_sale(db: Session, sale_id: int, data: SaleUpdate) -> Sale:
    sale = get_sale(db, sale_id)
    item = db.query(Item).filter(Item.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")

    # Restore old stock
    old_item = db.query(Item).filter(Item.id == sale.item_id).first()
    if old_item:
        old_item.quantity += sale.quantity

    if item.quantity < data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente. Disponível: {item.quantity}",
        )

    sale.item_id = data.item_id
    sale.quantity = data.quantity
    sale.unit_price = item.price
    sale.total = round(item.price * data.quantity, 2)
    item.quantity -= data.quantity

    db.commit()
    db.refresh(sale)
    return sale


def patch_sale(db: Session, sale_id: int, data: SalePatch) -> Sale:
    sale = get_sale(db, sale_id)
    update_data = data.model_dump(exclude_unset=True)

    item_id = update_data.get("item_id", sale.item_id)
    quantity = update_data.get("quantity", sale.quantity)

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")

    # Restore old stock
    old_item = db.query(Item).filter(Item.id == sale.item_id).first()
    if old_item:
        old_item.quantity += sale.quantity

    if item.quantity < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente. Disponível: {item.quantity}",
        )

    sale.item_id = item_id
    sale.quantity = quantity
    sale.unit_price = item.price
    sale.total = round(item.price * quantity, 2)
    item.quantity -= quantity

    db.commit()
    db.refresh(sale)
    return sale


def delete_sale(db: Session, sale_id: int) -> None:
    sale = get_sale(db, sale_id)
    # Restore stock
    item = db.query(Item).filter(Item.id == sale.item_id).first()
    if item:
        item.quantity += sale.quantity
    db.delete(sale)
    db.commit()
