from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from typing import Annotated

# from dependencies import get_token_header
from database import SessionDep
from schemas import Food, FoodCreate, FoodPublic, FoodUpdate

router = APIRouter(
    prefix="/foods",
    tags=["Foods"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
    
)

@router.post("/", response_model=FoodPublic)
def create_food(food: FoodCreate, session: SessionDep):
    db_food = Food.model_validate(food)
    session.add(db_food)
    session.commit()
    session.refresh(db_food)
    return db_food


@router.get("/", response_model=list[FoodPublic])
def read_food(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    food = session.exec(select(Food).offset(offset).limit(limit)).all()
    return food


@router.get("/{food_id}", response_model=FoodPublic)
def read_food(food_id: int, session: SessionDep):
    food = session.get(Food, food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    return food


@router.patch("/{food_id}", response_model=FoodPublic)
def update_food(food_id: int, food: FoodUpdate, session: SessionDep):
    food_db = session.get(Food, food_id)
    if not food_db:
        raise HTTPException(status_code=404, detail="Food not found")
    food_data = food.model_dump(exclude_unset=True)
    food_db.sqlmodel_update(food_data)
    session.add(food_db)
    session.commit()
    session.refresh(food_db)
    return food_db


@router.delete("/{food_id}")
def delete_food(food_id: int, session: SessionDep):
    food = session.get(Food, food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    session.delete(food)
    session.commit()
    return {"ok": True}