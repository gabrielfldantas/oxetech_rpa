from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from db import Base, engine, get_db
from models import Pessoa
from schemas import PessoaIn, PessoaOut, PessoaUpdate


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="p4_crud pessoas", lifespan=lifespan)


@app.post("/pessoas", response_model=PessoaOut, status_code=201)
def create(payload: PessoaIn, db: Session = Depends(get_db)):
    p = Pessoa(**payload.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.get("/pessoas", response_model=list[PessoaOut])
def list_all(db: Session = Depends(get_db)):
    return db.query(Pessoa).all()


@app.get("/pessoas/{pessoa_id}", response_model=PessoaOut)
def get_one(pessoa_id: int, db: Session = Depends(get_db)):
    p = db.get(Pessoa, pessoa_id)
    if not p:
        raise HTTPException(404, "pessoa not found")
    return p


@app.patch("/pessoas/{pessoa_id}", response_model=PessoaOut)
def update(pessoa_id: int, payload: PessoaUpdate, db: Session = Depends(get_db)):
    p = db.get(Pessoa, pessoa_id)
    if not p:
        raise HTTPException(404, "pessoa not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@app.delete("/pessoas/{pessoa_id}", status_code=204)
def delete(pessoa_id: int, db: Session = Depends(get_db)):
    p = db.get(Pessoa, pessoa_id)
    if not p:
        raise HTTPException(404, "pessoa not found")
    db.delete(p)
    db.commit()
