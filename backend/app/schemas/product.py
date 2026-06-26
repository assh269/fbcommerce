from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "MMK"
    stock: int = 0
    gender: Optional[str] = None
    target_age: Optional[str] = None
    category_id: Optional[UUID] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    stock: Optional[int] = None
    gender: Optional[str] = None
    target_age: Optional[str] = None
    is_active: Optional[bool] = None
    category_id: Optional[UUID] = None


class ProductImageOut(BaseModel):
    id: UUID
    url: str
    is_primary: bool

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    id: UUID
    seller_id: UUID
    category_id: Optional[UUID]
    name: str
    description: Optional[str]
    price: float
    currency: str
    stock: int
    gender: Optional[str]
    target_age: Optional[str]
    is_active: bool
    created_at: datetime
    images: list[ProductImageOut] = []

    class Config:
        from_attributes = True
