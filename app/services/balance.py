from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app import models


class HeatBalanceService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_balance(
        self, period_start: datetime, period_end: datetime
    ) -> dict:
        query_supply_heat = select(
            func.coalesce(func.sum(models.HeatReading.heat_supplied_gcal), 0.0)
        ).where(
            models.HeatReading.recorded_at.between(period_start, period_end)
        )
        result = await self.db.execute(query_supply_heat)
        total_supplied = result.scalar()

        query_consumed = select(
            func.coalesce(func.sum(models.MeterReading.heat_amount_gcal), 0.0)
        ).where(
            models.MeterReading.recorded_at.between(period_start, period_end)
        )
        result = await self.db.execute(query_consumed)
        total_consumed = result.scalar()

        loss = round(total_supplied - total_consumed, 4)
        loss_percent = round(
            (loss / total_supplied * 100) if total_supplied > 0 else 0.0, 2
        )
        tolerance = total_supplied * 0.05
        is_balanced = abs(loss) <= tolerance

        balance_record = models.HeatBalanceResult(
            period_start=period_start,
            period_end=period_end,
            total_supplied_gcal=total_supplied,
            total_consumed_gcal=total_consumed,
            loss_gcal=loss,
            loss_percent=loss_percent,
            is_balanced=int(is_balanced),
        )
        self.db.add(balance_record)
        await self.db.commit()
        await self.db.refresh(balance_record)

        return {
            "period_start": period_start,
            "period_end": period_end,
            "total_supplied_gcal": total_supplied,
            "total_consumed_gcal": total_consumed,
            "loss_gcal": loss,
            "loss_percent": loss_percent,
            "is_balanced": is_balanced,
        }

    async def get_consumer_consumption(
        self, consumer_id: int, period_start: datetime, period_end: datetime
    ) -> Optional[float]:
        query = select(
            func.coalesce(func.sum(models.MeterReading.heat_amount_gcal), 0.0)
        ).join(
            models.MeteringUnit,
            models.MeterReading.metering_unit_id == models.MeteringUnit.id,
        ).where(
            models.MeteringUnit.consumer_id == consumer_id,
            models.MeterReading.recorded_at.between(period_start, period_end),
        )
        result = await self.db.execute(query)
        return result.scalar()

    async def get_heat_loss_analysis(
        self, period_start: datetime, period_end: datetime
    ) -> dict:
        balance = await self.calculate_balance(period_start, period_end)
        top_consumers_query = (
            select(
                models.Consumer.id,
                models.Consumer.name,
                func.coalesce(func.sum(models.MeterReading.heat_amount_gcal), 0.0).label("consumed"),
            )
            .join(models.MeteringUnit, models.Consumer.id == models.MeteringUnit.consumer_id)
            .join(models.MeterReading, models.MeterReading.metering_unit_id == models.MeteringUnit.id)
            .where(models.MeterReading.recorded_at.between(period_start, period_end))
            .group_by(models.Consumer.id, models.Consumer.name)
            .order_by(func.coalesce(func.sum(models.MeterReading.heat_amount_gcal), 0.0).desc())
            .limit(5)
        )
        result = await self.db.execute(top_consumers_query)
        top_consumers = [{"id": row[0], "name": row[1], "consumed_gcal": float(row[2])} for row in result]

        return {
            "balance": balance,
            "top_consumers": top_consumers,
        }
