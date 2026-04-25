from datetime import datetime

from pydantic import BaseModel, Field


class SaleCreate(BaseModel):
    item_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=1_000_000)


class SaleUpdate(BaseModel):
    item_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=1_000_000)


class SalePatch(BaseModel):
    item_id: int | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, gt=0, le=1_000_000)


class SaleResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    quantity: int
    unit_price: float
    total: float
    created_at: datetime

    model_config = {"from_attributes": True}
