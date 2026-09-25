"""HTTP request and response schemas; domain objects stay framework agnostic."""

from datetime import date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator

from app.domain.entities import BirthPlaceCandidate, Client, ClientOverview
from lilly_scoring.models import LillyScoreResult, ScoreItem


class BirthPlaceCandidateResponse(BaseModel):
    id: str
    name: str
    display_name: str
    admin1: str | None
    admin2: str | None
    country: str
    country_code: str
    latitude: Decimal
    longitude: Decimal
    timezone: str

    @classmethod
    def from_domain(cls, place: BirthPlaceCandidate) -> "BirthPlaceCandidateResponse":
        return cls(
            id=place.provider_id,
            name=place.name,
            display_name=place.display_name,
            admin1=place.admin1,
            admin2=place.admin2,
            country=place.country,
            country_code=place.country_code,
            latitude=place.latitude,
            longitude=place.longitude,
            timezone=place.timezone,
        )


class BirthPlaceSearchResponse(BaseModel):
    items: list[BirthPlaceCandidateResponse]


class ClientCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    birth_date: date
    birth_time: time | None = None
    birth_place: str = Field(min_length=1, max_length=255)
    birth_latitude: Decimal = Field(ge=-90, le=90, decimal_places=6)
    birth_longitude: Decimal = Field(ge=-180, le=180, decimal_places=6)
    birth_timezone: str = Field(max_length=100)

    @field_validator("birth_timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError("Use a valid IANA time zone, for example Asia/Tokyo") from exc
        return value

    def to_domain(self) -> Client:
        return Client(**self.model_dump())


class ClientDetailResponse(BaseModel):
    id: int
    name: str
    birth_date: date
    birth_time: time | None
    birth_place: str
    birth_latitude: Decimal
    birth_longitude: Decimal
    birth_timezone: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_domain(cls, client: Client) -> "ClientDetailResponse":
        return cls(**{field: getattr(client, field) for field in cls.model_fields})


class ClientOverviewResponse(BaseModel):
    id: int
    name: str
    birth_date: date
    birth_time: time | None
    birth_place: str
    updated_at: datetime | None
    has_chart: bool
    sun_sign: str | None
    moon_sign: str | None
    ascendant_sign: str | None

    @classmethod
    def from_domain(cls, overview: ClientOverview) -> "ClientOverviewResponse":
        return cls(
            id=overview.client.id or 0, name=overview.client.name,
            birth_date=overview.client.birth_date,
            birth_time=overview.client.birth_time,
            birth_place=overview.client.birth_place,
            updated_at=overview.client.updated_at,
            has_chart=overview.has_chart,
            sun_sign=overview.signature.sun_sign,
            moon_sign=overview.signature.moon_sign,
            ascendant_sign=overview.signature.ascendant_sign,
        )


class ClientListResponse(BaseModel):
    items: list[ClientOverviewResponse]
    total: int


class ChartRead(BaseModel):
    client_id: int
    calculation_version: str
    calculation: dict


class ClientProfileResponse(BaseModel):
    client: ClientDetailResponse
    chart: ChartRead | None


class LillyScoreItemResponse(BaseModel):
    code: str
    label: str
    points: int
    description: str
    status: str
    related_body: str | None

    @classmethod
    def from_domain(cls, item: ScoreItem) -> "LillyScoreItemResponse":
        return cls(**{field: getattr(item, field) for field in cls.model_fields})


class LillyScoreSectionResponse(BaseModel):
    total: int
    items: list[LillyScoreItemResponse]


class LillyPlanetScoreResponse(BaseModel):
    planet: str
    essential: LillyScoreSectionResponse
    accidental: LillyScoreSectionResponse
    total: int


class LillyScoreResponse(BaseModel):
    sect: str
    planets: list[LillyPlanetScoreResponse]
    essential_total: int
    accidental_total: int
    grand_total: int
    warnings: list[str]

    @classmethod
    def from_domain(cls, result: LillyScoreResult) -> "LillyScoreResponse":
        planets = []
        for score in result.planets:
            essential = LillyScoreSectionResponse(
                total=score.essential.total,
                items=[LillyScoreItemResponse.from_domain(item) for item in score.essential.items],
            )
            accidental = LillyScoreSectionResponse(
                total=score.accidental.total,
                items=[LillyScoreItemResponse.from_domain(item) for item in score.accidental.items],
            )
            planets.append(LillyPlanetScoreResponse(
                planet=score.planet.value, essential=essential,
                accidental=accidental, total=score.total,
            ))
        return cls(
            sect=result.sect, planets=planets,
            essential_total=result.essential_total,
            accidental_total=result.accidental_total,
            grand_total=result.grand_total,
            warnings=list(result.warnings),
        )


class SessionOverviewResponse(BaseModel):
    id: int
    client_name: str
    held_at: datetime
    title: str


class DashboardResponse(BaseModel):
    client_count: int
    chart_count: int
    session_count: int
    recent_clients: list[ClientOverviewResponse]
    recent_sessions: list[SessionOverviewResponse]
