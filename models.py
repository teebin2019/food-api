
from sqlmodel import Field, SQLModel   

class FoodBase(SQLModel):
    name: str = Field(index=True)
    price: int = Field(index=True)

