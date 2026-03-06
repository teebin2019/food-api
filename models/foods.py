


# ──────────────────────────────────────────
# Base (shared fields)
# ──────────────────────────────────────────
from typing import Optional

from sqlmodel import Field, SQLModel


class FoodBase(SQLModel):
    name: str = Field(min_length=1, max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(gt=0)
    calories: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = Field(default=None)


# ──────────────────────────────────────────
# Table model (maps to DB)
# ──────────────────────────────────────────
class Food(FoodBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# ──────────────────────────────────────────
# Request / Response schemas
# ──────────────────────────────────────────
class FoodCreate(FoodBase):
    pass


class FoodUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    price: Optional[float] = Field(default=None, gt=0)
    calories: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = Field(default=None)


class FoodRead(FoodBase):
    id: int