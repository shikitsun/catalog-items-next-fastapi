from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter()

@router.post('/', response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create(payload: ItemCreate, db: AsyncSession = Depends(get_db())) ->  Item:
    item = Item(**payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.get('/all', response_model=list[ItemRead])
async def all(_: None, db: AsyncSession = Depends(get_db())) -> list[ItemRead]:
    result = await db.execute(select(ItemRead).order_by(Item.created_at.desc()))
    return list(result.scalars().all())

@router.patch("/{id}", response_model=ItemRead)
async def update(
    id: int, payload: ItemUpdate, db: AsyncSession = Depends(get_db)
) -> Item:
    item = await db.get(Item, id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item
