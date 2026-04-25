from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import VALID_ROLES
from app.models.user import User
from app.schemas.user import UserCreate, UserPatch, UserUpdate


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user


def create_user(db: Session, data: UserCreate) -> User:
    if data.role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role inválida. Opções: {', '.join(sorted(VALID_ROLES))}",
        )
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email já cadastrado"
        )
    user = User(**data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    user = get_user(db, user_id)
    if data.role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role inválida. Opções: {', '.join(sorted(VALID_ROLES))}",
        )
    existing = db.query(User).filter(User.email == data.email, User.id != user_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já cadastrado")
    for key, value in data.model_dump().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def patch_user(db: Session, user_id: int, data: UserPatch) -> User:
    user = get_user(db, user_id)
    update_data = data.model_dump(exclude_unset=True)
    if "role" in update_data and update_data["role"] not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role inválida. Opções: {', '.join(sorted(VALID_ROLES))}",
        )
    if "email" in update_data:
        existing = db.query(User).filter(User.email == update_data["email"], User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já cadastrado")
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()
