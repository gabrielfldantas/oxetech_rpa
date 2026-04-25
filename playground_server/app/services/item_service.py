from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemPatch, ItemUpdate


def list_items(db: Session, skip: int = 0, limit: int = 100) -> list[Item]:
    return db.query(Item).offset(skip).limit(limit).all()


def get_item(db: Session, item_id: int) -> Item:
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    return item


def create_item(db: Session, data: ItemCreate) -> Item:
    item = Item(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item_id: int, data: ItemUpdate) -> Item:
    item = get_item(db, item_id)
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def patch_item(db: Session, item_id: int, data: ItemPatch) -> Item:
    item = get_item(db, item_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item_id: int) -> None:
    item = get_item(db, item_id)
    db.delete(item)
    db.commit()
