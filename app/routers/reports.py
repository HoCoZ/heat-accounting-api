from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.schemas import BalanceRequest, BalanceResponse
from app.services.balance import HeatBalanceService
from app.services.report_gen import ReportGenerator

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    period_start: datetime = Query(...),
    period_end: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
):
    service = HeatBalanceService(db)
    balance = await service.calculate_balance(period_start, period_end)

    consumer_result = await service.get_heat_loss_analysis(period_start, period_end)

    return BalanceResponse(
        period_start=balance["period_start"],
        period_end=balance["period_end"],
        total_supplied_gcal=balance["total_supplied_gcal"],
        total_consumed_gcal=balance["total_consumed_gcal"],
        loss_gcal=balance["loss_gcal"],
        loss_percent=balance["loss_percent"],
        is_balanced=balance["is_balanced"],
    )


@router.post("/generate-act")
async def generate_act(
    request: BalanceRequest,
    db: AsyncSession = Depends(get_db),
):
    service = HeatBalanceService(db)
    balance = await service.calculate_balance(request.period_start, request.period_end)
    analysis = await service.get_heat_loss_analysis(request.period_start, request.period_end)

    doc_bytes = ReportGenerator.generate_balance_act(
        period_start=request.period_start,
        period_end=request.period_end,
        total_supplied=balance["total_supplied_gcal"],
        total_consumed=balance["total_consumed_gcal"],
        loss=balance["loss_gcal"],
        loss_percent=balance["loss_percent"],
        is_balanced=balance["is_balanced"],
        consumer_details=analysis["top_consumers"],
    )

    filename = f"act_{request.period_start.strftime('%Y%m%d')}_{request.period_end.strftime('%Y%m%d')}.docx"

    return Response(
        content=doc_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
