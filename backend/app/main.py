"""FastAPI composition root connecting use cases to concrete adapters."""

from collections.abc import Generator

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.application.use_cases import (
    CalculateLillyScore, ChartCalculationError, ChartNotFoundError, ClientNotFoundError,
    CreateClient, ExportNatalChartSummary, GetClientProfile, GetDashboard,
    GetOrCreateNatalChart, LillyScoreCalculationError, ListClients, LocationSearchError,
    SearchBirthPlaces,
)
from app.db import SessionLocal
from app.infrastructure.chart_calculator import KerykeionNatalChartCalculator
from app.infrastructure.geocoding import OpenMeteoGeocodingProvider
from app.infrastructure.markdown_chart_summary import MarkdownChartSummaryRenderer
from app.infrastructure.lilly_score_adapter import CachedChartLillyScoreCalculator
from app.infrastructure.repositories import SqlAlchemyClientRepository
from app.presentation.schemas import (
    BirthPlaceCandidateResponse, BirthPlaceSearchResponse, ChartRead,
    ClientCreateRequest, ClientDetailResponse, ClientListResponse, ClientProfileResponse,
    ClientOverviewResponse, DashboardResponse, LillyScoreResponse,
)

app = FastAPI(
    title="占星術リーディング補助アプリ API",
    description="Kerykeion を使用したネイタルチャート計算・クライアント管理 API",
    version="0.2.0",
)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as db:
        yield db


def get_clients(db: Session = Depends(get_db)) -> SqlAlchemyClientRepository:
    return SqlAlchemyClientRepository(db)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/locations/search", response_model=BirthPlaceSearchResponse)
def search_birth_places(
    q: str = Query(min_length=2, max_length=200),
) -> BirthPlaceSearchResponse:
    try:
        items = SearchBirthPlaces(OpenMeteoGeocodingProvider()).execute(q)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except LocationSearchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return BirthPlaceSearchResponse(
        items=[BirthPlaceCandidateResponse.from_domain(item) for item in items]
    )


@app.get("/dashboard", response_model=DashboardResponse)
def read_dashboard(
    clients: SqlAlchemyClientRepository = Depends(get_clients),
) -> DashboardResponse:
    result = GetDashboard(clients).execute()
    return DashboardResponse(
        **{key: result[key] for key in ("client_count", "chart_count", "session_count")},
        recent_clients=[ClientOverviewResponse.from_domain(item) for item in result["recent_clients"]],
        recent_sessions=result["recent_sessions"],
    )


@app.get("/clients", response_model=ClientListResponse)
def list_clients(
    search: str | None = Query(default=None, max_length=200),
    sign: str | None = Query(default=None, max_length=30),
    clients: SqlAlchemyClientRepository = Depends(get_clients),
) -> ClientListResponse:
    items = ListClients(clients).execute(search=search, sign=sign)
    return ClientListResponse(
        items=[ClientOverviewResponse.from_domain(item) for item in items],
        total=len(items),
    )


@app.post("/clients", response_model=ClientDetailResponse, status_code=201)
def create_client(
    payload: ClientCreateRequest,
    clients: SqlAlchemyClientRepository = Depends(get_clients),
) -> ClientDetailResponse:
    client = CreateClient(clients).execute(payload.to_domain())
    return ClientDetailResponse.from_domain(client)


@app.get("/clients/{client_id}", response_model=ClientProfileResponse)
def read_client_profile(
    client_id: int,
    clients: SqlAlchemyClientRepository = Depends(get_clients),
) -> ClientProfileResponse:
    try:
        profile = GetClientProfile(clients).execute(client_id)
    except ClientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    chart = (
        ChartRead(
            client_id=profile.chart.client_id,
            calculation_version=profile.chart.calculation_version,
            calculation=profile.chart.calculation,
        )
        if profile.chart
        else None
    )
    return ClientProfileResponse(
        client=ClientDetailResponse.from_domain(profile.client),
        chart=chart,
    )


@app.get("/clients/{client_id}/chart", response_model=ChartRead)
def read_chart(
    client_id: int,
    clients: SqlAlchemyClientRepository = Depends(get_clients),
) -> ChartRead:
    try:
        chart = GetOrCreateNatalChart(
            clients, KerykeionNatalChartCalculator()
        ).execute(client_id)
    except ClientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ChartCalculationError, ValueError) as exc:
        clients.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ChartRead(
        client_id=chart.client_id,
        calculation_version=chart.calculation_version,
        calculation=chart.calculation,
    )


@app.get("/clients/{client_id}/chart/summary")
def export_chart_summary(
    client_id: int,
    clients: SqlAlchemyClientRepository = Depends(get_clients),
) -> Response:
    try:
        summary = ExportNatalChartSummary(
            clients, MarkdownChartSummaryRenderer()
        ).execute(client_id)
    except ClientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ChartNotFoundError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return Response(content=summary.content, media_type=summary.media_type)


@app.get("/clients/{client_id}/chart/lilly-score", response_model=LillyScoreResponse)
def calculate_lilly_score(
    client_id: int,
    clients: SqlAlchemyClientRepository = Depends(get_clients),
) -> LillyScoreResponse:
    try:
        result = CalculateLillyScore(
            clients, CachedChartLillyScoreCalculator()
        ).execute(client_id)
    except ClientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ChartNotFoundError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except LillyScoreCalculationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return LillyScoreResponse.from_domain(result)
