from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class Pessoa(Base):
    __tablename__ = "pessoas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    primeiro_nome: Mapped[str] = mapped_column(String(80), nullable=False)
    segundo_nome: Mapped[str] = mapped_column(String(80), nullable=False)
    pais: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
