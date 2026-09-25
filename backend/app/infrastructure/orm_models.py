"""SQLAlchemy persistence models. They do not leak into the domain layer."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Time, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    birth_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    birth_place: Mapped[str] = mapped_column(String(255), nullable=False)
    birth_latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    birth_longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    birth_timezone: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    chart: Mapped["Chart | None"] = relationship(back_populates="client", uselist=False, cascade="all, delete-orphan")


class Chart(Base):
    __tablename__ = "charts"
    __table_args__ = (UniqueConstraint("client_id", name="uq_charts_client_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    calculation: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    calculation_version: Mapped[str] = mapped_column(String(50), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    client: Mapped[Client] = relationship(back_populates="chart")
    memos: Mapped[list["ChartInterpretationMemo"]] = relationship(back_populates="chart", cascade="all, delete-orphan")


class ChartInterpretationMemo(Base):
    __tablename__ = "chart_interpretation_memos"
    __table_args__ = (UniqueConstraint("chart_id", "planet", name="uq_chart_memos_chart_planet"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chart_id: Mapped[int] = mapped_column(ForeignKey("charts.id", ondelete="CASCADE"), nullable=False)
    planet: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    chart: Mapped[Chart] = relationship(back_populates="memos")
