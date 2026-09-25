"""Compatibility wrapper around the chart application use case."""

from sqlalchemy.orm import Session

from app.application.use_cases import GetOrCreateNatalChart
from app.infrastructure.chart_calculator import KerykeionNatalChartCalculator
from app.infrastructure.repositories import SqlAlchemyClientRepository


def get_or_create_natal_chart(db: Session, client_id: int):
    return GetOrCreateNatalChart(
        SqlAlchemyClientRepository(db), KerykeionNatalChartCalculator()
    ).execute(client_id)
