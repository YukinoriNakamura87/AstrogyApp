"""SQLAlchemy implementation of the domain repository contract."""

from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.domain.entities import ChartInterpretationMemo, ChartSignature, Client, ClientOverview, NatalChart
from app.infrastructure import orm_models


def _client_entity(row: orm_models.Client) -> Client:
    return Client(
        id=row.id, name=row.name, birth_date=row.birth_date,
        birth_time=row.birth_time, birth_place=row.birth_place,
        birth_latitude=row.birth_latitude, birth_longitude=row.birth_longitude,
        birth_timezone=row.birth_timezone, created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _chart_entity(row: orm_models.Chart) -> NatalChart:
    return NatalChart(
        id=row.id, client_id=row.client_id, calculation=row.calculation,
        calculation_version=row.calculation_version,
        calculated_at=row.calculated_at,
    )


def _memo_entity(row: orm_models.ChartInterpretationMemo) -> ChartInterpretationMemo:
    return ChartInterpretationMemo(
        id=row.id, chart_id=row.chart_id, planet=row.planet, content=row.content,
        created_at=row.created_at, updated_at=row.updated_at,
    )


def _signature(calculation: dict[str, Any] | None) -> ChartSignature:
    if not calculation:
        return ChartSignature()
    subject = calculation.get("subject", {})
    points = subject.values() if isinstance(subject, dict) else []
    signs: dict[str, str] = {}
    for point in points:
        if not isinstance(point, dict):
            continue
        name = str(point.get("name", "")).replace("_", "").casefold()
        sign = point.get("sign")
        if sign and name in {"sun", "moon", "ascendant", "asc"}:
            signs[name] = str(sign)
    return ChartSignature(
        sun_sign=signs.get("sun"), moon_sign=signs.get("moon"),
        ascendant_sign=signs.get("ascendant") or signs.get("asc"),
    )


class SqlAlchemyClientRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, client: Client) -> Client:
        row = orm_models.Client(
            name=client.name, birth_date=client.birth_date,
            birth_time=client.birth_time, birth_place=client.birth_place,
            birth_latitude=client.birth_latitude,
            birth_longitude=client.birth_longitude,
            birth_timezone=client.birth_timezone,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return _client_entity(row)

    def get(self, client_id: int, *, for_update: bool = False) -> Client | None:
        statement = select(orm_models.Client).where(orm_models.Client.id == client_id)
        if for_update:
            statement = statement.with_for_update()
        row = self.db.scalar(statement)
        return _client_entity(row) if row else None

    def list_overviews(self, search: str | None = None) -> list[ClientOverview]:
        statement = (
            select(orm_models.Client)
            .options(joinedload(orm_models.Client.chart))
            .order_by(orm_models.Client.updated_at.desc(), orm_models.Client.id.desc())
        )
        if search and search.strip():
            term = f"%{search.strip()}%"
            statement = statement.where(
                or_(orm_models.Client.name.ilike(term), orm_models.Client.birth_place.ilike(term))
            )
        rows = self.db.scalars(statement).unique().all()
        return [
            ClientOverview(
                client=_client_entity(row), has_chart=row.chart is not None,
                signature=_signature(row.chart.calculation if row.chart else None),
            )
            for row in rows
        ]

    def count(self) -> int:
        return self.db.scalar(select(func.count(orm_models.Client.id))) or 0

    def count_with_chart(self) -> int:
        return self.db.scalar(select(func.count(orm_models.Chart.id))) or 0

    def get_chart(self, client_id: int) -> NatalChart | None:
        row = self.db.scalar(select(orm_models.Chart).where(orm_models.Chart.client_id == client_id))
        return _chart_entity(row) if row else None

    def save_chart(self, chart: NatalChart) -> NatalChart:
        row = orm_models.Chart(
            client_id=chart.client_id, calculation=chart.calculation,
            calculation_version=chart.calculation_version,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return _chart_entity(row)

    def list_chart_memos(self, client_id: int) -> list[ChartInterpretationMemo]:
        rows = self.db.scalars(
            select(orm_models.ChartInterpretationMemo)
            .join(orm_models.Chart)
            .where(orm_models.Chart.client_id == client_id)
            .order_by(orm_models.ChartInterpretationMemo.id)
        ).all()
        return [_memo_entity(row) for row in rows]

    def upsert_chart_memos(
        self, client_id: int, memos: list[ChartInterpretationMemo]
    ) -> list[ChartInterpretationMemo]:
        chart_row = self.db.scalar(
            select(orm_models.Chart).where(orm_models.Chart.client_id == client_id)
        )
        if chart_row is None:
            return []

        existing = {
            row.planet: row
            for row in self.db.scalars(
                select(orm_models.ChartInterpretationMemo).where(
                    orm_models.ChartInterpretationMemo.chart_id == chart_row.id
                )
            ).all()
        }
        for memo in memos:
            row = existing.get(memo.planet)
            if not memo.content:
                if row is not None:
                    self.db.delete(row)
                continue
            if row is None:
                self.db.add(orm_models.ChartInterpretationMemo(
                    chart_id=chart_row.id, planet=memo.planet, content=memo.content,
                ))
            else:
                row.content = memo.content
        self.db.commit()
        return self.list_chart_memos(client_id)

    def rollback(self) -> None:
        self.db.rollback()
