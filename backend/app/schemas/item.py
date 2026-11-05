import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class ItemBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=200)

class ItemRead(ItemBase):
    id: uuid.UUID
    preview_url: str
    created_at: datetime
