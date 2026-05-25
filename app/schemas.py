from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models import ConsumerType


class ConsumerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = None
    contract_number: str = Field(..., min_length=1, max_length=50)
    consumer_type: ConsumerType = ConsumerType.RESIDENTIAL
    heat_supply_area: Optional[float] = None


class ConsumerResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    contract_number: str
    consumer_type: ConsumerType
    heat_supply_area: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class MeterReadingCreate(BaseModel):
    metering_unit_id: int
    heat_amount_gcal: float = Field(..., ge=0)
    coolant_temperature_supply: Optional[float] = None
    coolant_temperature_return: Optional[float] = None
    coolant_pressure_supply: Optional[float] = None
    coolant_pressure_return: Optional[float] = None
    coolant_flow_rate: Optional[float] = None


class MeterReadingResponse(BaseModel):
    id: int
    metering_unit_id: int
    recorded_at: datetime
    heat_amount_gcal: float
    coolant_temperature_supply: Optional[float]
    coolant_temperature_return: Optional[float]

    model_config = {"from_attributes": True}


class BalanceRequest(BaseModel):
    period_start: datetime
    period_end: datetime


class BalanceResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    total_supplied_gcal: float
    total_consumed_gcal: float
    loss_gcal: float
    loss_percent: float
    is_balanced: bool
