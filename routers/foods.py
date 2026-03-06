from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from database import get_session
from models.foods import Food, FoodCreate, FoodRead, FoodUpdate


router = APIRouter(
    prefix="/api/foods",
    tags=["Foods"],
)


# ──────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────
@router.post("/", response_model=FoodRead, status_code=status.HTTP_201_CREATED)
def create_food(food: FoodCreate, session: Session = Depends(get_session)):
    db_food = Food.model_validate(food)
    session.add(db_food)
    session.commit()
    session.refresh(db_food)
    return db_food


# ──────────────────────────────────────────
# READ ALL (with pagination + search)
# ──────────────────────────────────────────
@router.get("/", response_model=List[FoodRead])
def list_foods(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    name: Optional[str] = Query(default=None, description="ค้นหาชื่ออาหาร"),
    session: Session = Depends(get_session),
):
    query = select(Food)
    if name:
        query = query.where(Food.name.contains(name))
    foods = session.exec(query.offset(offset).limit(limit)).all()
    return foods


# ──────────────────────────────────────────
# READ ONE
# ──────────────────────────────────────────
@router.get("/{food_id}", response_model=FoodRead)
def get_food(food_id: int, session: Session = Depends(get_session)):
    food = session.get(Food, food_id)
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ไม่พบอาหาร id={food_id}",
        )
    return food


# ──────────────────────────────────────────
# UPDATE (PATCH — อัปเดตเฉพาะ field ที่ส่งมา)
# ──────────────────────────────────────────
@router.patch("/{food_id}", response_model=FoodRead)
def update_food(
    food_id: int,
    food_update: FoodUpdate,
    session: Session = Depends(get_session),
):
    food = session.get(Food, food_id)
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ไม่พบอาหาร id={food_id}",
        )

    update_data = food_update.model_dump(exclude_unset=True)
    food.sqlmodel_update(update_data)
    session.add(food)
    session.commit()
    session.refresh(food)
    return food


# ──────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────
@router.delete("/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food(food_id: int, session: Session = Depends(get_session)):
    food = session.get(Food, food_id)
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ไม่พบอาหาร id={food_id}",
        )
    session.delete(food)
    session.commit()