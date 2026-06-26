from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SellerCreate(BaseModel):
    telegram_id: int
    business_name: str
    username: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None


class SellerUpdate(BaseModel):
    business_name: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None


class SellerOut(BaseModel):
    id: UUID
    telegram_id: int
    username: Optional[str]
    business_name: str
    phone: Optional[str]
    description: Optional[str]
    rating: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
