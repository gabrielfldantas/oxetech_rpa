from pydantic import BaseModel, ConfigDict


class PessoaIn(BaseModel):
    primeiro_nome: str
    segundo_nome: str
    pais: str
    status: str = "active"


class PessoaUpdate(BaseModel):
    primeiro_nome: str | None = None
    segundo_nome: str | None = None
    pais: str | None = None
    status: str | None = None


class PessoaOut(PessoaIn):
    id: int
    model_config = ConfigDict(from_attributes=True)
