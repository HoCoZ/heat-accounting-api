from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional

from app.database import get_db
from app import models
from app import schemas

router = APIRouter(prefix="/api/v1/readings", tags=["readings"])


@router.get("", response_model=list[schemas.MeterReadingResponse])
async def list_readings(
    metering_unit_id: Optional[int] = Query(None),
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(models.MeterReading)
    if metering_unit_id:
        stmt = stmt.where(models.MeterReading.metering_unit_id == metering_unit_id)
    if period_start:
        stmt = stmt.where(models.MeterReading.recorded_at >= period_start)
    if period_end:
        stmt = stmt.where(models.MeterReading.recorded_at <= period_end)
    stmt = stmt.order_by(models.MeterReading.recorded_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=schemas.MeterReadingResponse, status_code=201)
async def create_reading(data: schemas.MeterReadingCreate, db: AsyncSession = Depends(get_db)):
    unit_result = await db.execute(
        select(models.MeteringUnit).where(models.MeteringUnit.id == data.metering_unit_id)
    )
    if not unit_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Metering unit not found")

    reading = models.MeterReading(**data.model_dump())
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    return reading
