import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, status, UploadFile
from fastapi.params import Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.main import settings
from app.models.item import Item
from app.schemas.item import ItemRead, ItemUpdate
from app.services.file import upload_file

router = APIRouter()

@router.post('/', response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    x_admin_token: Header | None = None
) -> Item:
    if x_admin_token != settings.internal_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    preview_url = upload_file(file)
    item = Item(title=title, preview_url=preview_url)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.get("/{id}", response_model=ItemRead)
async def get(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ItemRead:
    item = await db.get(Item, id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/all", response_model=list[ItemRead])
async def list_all(
    _: None,
    db: AsyncSession = Depends(get_db),
) -> list[ItemRead]:
    result = await db.execute(select(Item).order_by(Item.created_at.desc()))
    return list(result.scalars().all())

@router.patch("/{id}", response_model=ItemRead)
async def update(
    id: uuid.UUID,
    payload: ItemUpdate,
    db: AsyncSession = Depends(get_db),
) -> Item:
    item = await db.get(Item, id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item
