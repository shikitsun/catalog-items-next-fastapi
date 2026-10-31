from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ItemBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    preview_url: str | None = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=200)

class ItemRead(ItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
