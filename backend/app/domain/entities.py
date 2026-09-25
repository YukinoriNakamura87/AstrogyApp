"""Core business objects for clients and cached natal charts."""

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any


@dataclass(slots=True)
class Client:
    name: str
    birth_date: date
    birth_time: time | None
    birth_place: str
    birth_latitude: Decimal
    birth_longitude: Decimal
    birth_timezone: str
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class NatalChart:
    client_id: int
    calculation: dict[str, Any]
    calculation_version: str
    id: int | None = None
    calculated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class ChartSummary:
    """Portable text representation of a calculated natal chart."""

    content: str
    media_type: str
    file_extension: str


@dataclass(frozen=True, slots=True)
class ChartSignature:
    sun_sign: str | None = None
    moon_sign: str | None = None
    ascendant_sign: str | None = None


@dataclass(frozen=True, slots=True)
class ClientOverview:
    client: Client
    has_chart: bool
    signature: ChartSignature


@dataclass(frozen=True, slots=True)
class ClientProfile:
    client: Client
    chart: NatalChart | None


@dataclass(frozen=True, slots=True)
class BirthPlaceCandidate:
    """A selectable place resolved to the data required for chart calculation."""

    provider_id: str
    name: str
    country: str
    country_code: str
    latitude: Decimal
    longitude: Decimal
    timezone: str
    admin1: str | None = None
    admin2: str | None = None

    @property
    def display_name(self) -> str:
        parts = [self.name, self.admin2, self.admin1, self.country]
        return "、".join(dict.fromkeys(part for part in parts if part))
