import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, status, UploadFile
from fastapi.params import Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import get_settings
from app.models.item import Item
from app.schemas.item import ItemRead, ItemUpdate
from app.services.file import (
    EmptyUploadError,
    UnsupportedMediaTypeError,
    UploadTooLargeError,
    presigned_url,
    upload_file,
)

router = APIRouter()
settings = get_settings()

def map_into_read(item: Item) -> ItemRead:
    return ItemRead(
        id=item.id,
        title=item.title,
        preview_url=presigned_url(item.preview_url),
        created_at=item.created_at,
    )

# here used HTTP_201_CREATED status, but in another places are just number
# ...oops?
@router.post('/', response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    x_admin_token: str | None = Header(default=None, alias="x-admin-token")
) -> ItemRead:
    if x_admin_token != settings.internal_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        preview_url = upload_file(file, max_bytes=settings.max_upload_bytes)
    except UploadTooLargeError as exc:
        raise HTTPException(
            status_code=413, detail=str(exc)
        ) from exc
    except UnsupportedMediaTypeError as exc:
        raise HTTPException(
            status_code=415, detail=str(exc)
        ) from exc
    except EmptyUploadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    item = Item(title=title, preview_url=preview_url)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return map_into_read(item)

@router.get("/all", response_model=list[ItemRead])
async def list_all(
    db: AsyncSession = Depends(get_db),
) -> list[ItemRead]:
    result = await db.execute(select(Item).order_by(Item.created_at.desc()))
    return [map_into_read(item) for item in result.scalars().all()]

@router.get("/{id}", response_model=ItemRead)
async def get(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ItemRead:
    item = await db.get(Item, id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return map_into_read(item)

@router.patch("/{id}", response_model=ItemRead)
async def update(
    id: uuid.UUID,
    payload: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    x_admin_token: str | None = Header(default=None, alias="x-admin-token")
) -> ItemRead:
    if x_admin_token != settings.internal_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    item = await db.get(Item, id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return map_into_read(item)
