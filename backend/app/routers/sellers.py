from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.seller import Seller
from app.schemas.seller import SellerCreate, SellerOut, SellerUpdate

router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.get("", response_model=list[SellerOut])
async def list_sellers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Seller).where(Seller.is_active == True))
    return result.scalars().all()


@router.get("/{seller_id}", response_model=SellerOut)
async def get_seller(seller_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Seller).where(Seller.id == seller_id))
    seller = result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return seller


@router.get("/telegram/{telegram_id}", response_model=SellerOut)
async def get_seller_by_telegram(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Seller).where(Seller.telegram_id == telegram_id))
    seller = result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return seller


@router.post("", response_model=SellerOut, status_code=status.HTTP_201_CREATED)
async def create_seller(data: SellerCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Seller).where(Seller.telegram_id == data.telegram_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Seller already registered")
    seller = Seller(**data.model_dump())
    db.add(seller)
    await db.commit()
    await db.refresh(seller)
    return seller


@router.patch("/{seller_id}", response_model=SellerOut)
async def update_seller(seller_id: UUID, data: SellerUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Seller).where(Seller.id == seller_id))
    seller = result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(seller, key, val)
    await db.commit()
    await db.refresh(seller)
    return seller
