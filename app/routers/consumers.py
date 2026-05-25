from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional

from app.database import get_db
from app import models
from app import schemas

router = APIRouter(prefix="/api/v1/consumers", tags=["consumers"])


@router.get("", response_model=list[schemas.ConsumerResponse])
async def list_consumers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Consumer).order_by(models.Consumer.name))
    return result.scalars().all()


@router.get("/{consumer_id}", response_model=schemas.ConsumerResponse)
async def get_consumer(consumer_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Consumer).where(models.Consumer.id == consumer_id))
    consumer = result.scalar_one_or_none()
    if not consumer:
        raise HTTPException(status_code=404, detail="Consumer not found")
    return consumer


@router.post("", response_model=schemas.ConsumerResponse, status_code=201)
async def create_consumer(data: schemas.ConsumerCreate, db: AsyncSession = Depends(get_db)):
    consumer = models.Consumer(**data.model_dump())
    db.add(consumer)
    await db.commit()
    await db.refresh(consumer)
    return consumer
