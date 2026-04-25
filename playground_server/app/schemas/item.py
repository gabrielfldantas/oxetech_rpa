from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    price: float = Field(gt=0)
    quantity: int = Field(default=0, ge=0)


class ItemUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)


class ItemPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    price: float | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, ge=0)


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    quantity: int

    model_config = {"from_attributes": True}
