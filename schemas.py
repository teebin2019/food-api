from sqlmodel import Field

from models import FoodBase

class Food(FoodBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    is_sell: bool = Field(default=False)

class FoodPublic(FoodBase):
    id: int
    is_sell: bool

class FoodCreate(FoodBase):
    is_sell: bool = Field(default=False)

class FoodUpdate(FoodBase):
    name: str | None = None
    price: int | None = None
    is_sell: bool = Field(default=False)