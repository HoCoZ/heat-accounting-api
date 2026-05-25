from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.database import Base


class ConsumerType(str, enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"


class Consumer(Base):
    __tablename__ = "consumers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    contract_number = Column(String(50), unique=True, nullable=False)
    consumer_type = Column(SAEnum(ConsumerType), default=ConsumerType.RESIDENTIAL)
    heat_supply_area = Column(Float, comment="площадь отапливаемого здания, кв.м")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    metering_units = relationship("MeteringUnit", back_populates="consumer")
    readings = relationship("HeatReading", back_populates="consumer")


class MeteringUnit(Base):
    __tablename__ = "metering_units"

    id = Column(Integer, primary_key=True, index=True)
    consumer_id = Column(Integer, ForeignKey("consumers.id"), nullable=False)
    unit_number = Column(String(50), unique=True, nullable=False)
    model = Column(String(100))
    verification_date = Column(DateTime)
    installation_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    consumer = relationship("Consumer", back_populates="metering_units")
    readings = relationship("MeterReading", back_populates="metering_unit")


class MeterReading(Base):
    __tablename__ = "meter_readings"

    id = Column(Integer, primary_key=True, index=True)
    metering_unit_id = Column(Integer, ForeignKey("metering_units.id"), nullable=False)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    heat_amount_gcal = Column(Float, comment="количество тепла, Гкал")
    coolant_temperature_supply = Column(Float, comment="температура подачи, C")
    coolant_temperature_return = Column(Float, comment="температура обратки, C")
    coolant_pressure_supply = Column(Float, comment="давление подачи, кгс/см2")
    coolant_pressure_return = Column(Float, comment="давление обратки, кгс/см2")
    coolant_flow_rate = Column(Float, comment="расход теплоносителя, т/ч")

    metering_unit = relationship("MeteringUnit", back_populates="readings")


class HeatReading(Base):
    __tablename__ = "heat_readings"

    id = Column(Integer, primary_key=True, index=True)
    consumer_id = Column(Integer, ForeignKey("consumers.id"), nullable=False)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    heat_supplied_gcal = Column(Float, comment="отпущено тепла, Гкал")
    heat_consumed_gcal = Column(Float, comment="потреблено тепла, Гкал")

    consumer = relationship("Consumer", back_populates="readings")


class HeatBalanceResult(Base):
    __tablename__ = "heat_balance_results"

    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    total_supplied_gcal = Column(Float, default=0.0)
    total_consumed_gcal = Column(Float, default=0.0)
    loss_gcal = Column(Float, default=0.0)
    loss_percent = Column(Float, default=0.0)
    is_balanced = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
