from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewOut

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/product/{product_id}", response_model=list[ReviewOut])
async def list_product_reviews(product_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Review).where(Review.product_id == product_id).order_by(Review.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(data: ReviewCreate, db: AsyncSession = Depends(get_db)):
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    review = Review(**data.model_dump())
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review
