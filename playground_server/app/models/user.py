import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="viewer")
    api_key: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    sales: Mapped[list["Sale"]] = relationship(back_populates="user")  # noqa: F821
