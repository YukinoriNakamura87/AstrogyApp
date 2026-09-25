"""Use cases exposed by the current client-management slice."""

from dataclasses import dataclass

from app.domain.entities import BirthPlaceCandidate, ChartInterpretationMemo, ChartSummary, Client, ClientOverview, ClientProfile, NatalChart
from app.domain.repositories import ClientRepository
from app.domain.services import ChartSummaryRenderer, GeocodingProvider, GeocodingProviderError, NatalChartCalculator
from app.domain.services import LillyScoreCalculator
from lilly_scoring.models import LillyScoreResult


class ClientNotFoundError(Exception):
    pass


class ChartCalculationError(Exception):
    pass


class ChartNotFoundError(Exception):
    pass


class LillyScoreCalculationError(Exception):
    pass


class LocationSearchError(Exception):
    pass


SUPPORTED_MEMO_POINTS = (
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto", "Chiron", "True_North_Lunar_Node",
)


@dataclass(slots=True)
class SearchBirthPlaces:
    geocoding: GeocodingProvider

    def execute(self, query: str) -> list[BirthPlaceCandidate]:
        normalized = query.strip()
        if len(normalized) < 2:
            raise ValueError("出生地は2文字以上で入力してください")
        try:
            return self.geocoding.search(normalized)
        except GeocodingProviderError as exc:
            raise LocationSearchError("出生地検索サービスに接続できません") from exc
        except Exception as exc:
            raise LocationSearchError("出生地検索サービスに接続できません") from exc


@dataclass(slots=True)
class CreateClient:
    clients: ClientRepository

    def execute(self, client: Client) -> Client:
        return self.clients.add(client)


@dataclass(slots=True)
class GetClientProfile:
    clients: ClientRepository

    def execute(self, client_id: int) -> ClientProfile:
        client = self.clients.get(client_id)
        if client is None:
            raise ClientNotFoundError("Client not found")
        return ClientProfile(client=client, chart=self.clients.get_chart(client_id))


@dataclass(slots=True)
class ListClients:
    clients: ClientRepository

    def execute(self, search: str | None = None, sign: str | None = None) -> list[ClientOverview]:
        items = self.clients.list_overviews(search)
        if not sign:
            return items
        normalized = sign.casefold()
        return [
            item for item in items
            if normalized in {
                (item.signature.sun_sign or "").casefold(),
                (item.signature.moon_sign or "").casefold(),
                (item.signature.ascendant_sign or "").casefold(),
            }
        ]


@dataclass(slots=True)
class GetDashboard:
    clients: ClientRepository

    def execute(self) -> dict:
        return {
            "client_count": self.clients.count(),
            "chart_count": self.clients.count_with_chart(),
            # Session remains separate from chart memos and arrives with its feature.
            "session_count": 0,
            "recent_clients": self.clients.list_overviews()[:5],
            "recent_sessions": [],
        }


@dataclass(slots=True)
class GetOrCreateNatalChart:
    clients: ClientRepository
    calculator: NatalChartCalculator

    def execute(self, client_id: int) -> NatalChart:
        client = self.clients.get(client_id, for_update=True)
        if client is None:
            raise ClientNotFoundError("Client not found")
        cached = self.clients.get_chart(client_id)
        if cached is not None:
            return cached
        if client.birth_time is None:
            raise ChartCalculationError(
                "Birth time is required to calculate an accurate natal chart"
            )
        return self.clients.save_chart(self.calculator.calculate(client))


@dataclass(slots=True)
class GetChartInterpretationMemos:
    clients: ClientRepository

    def execute(self, client_id: int) -> list[ChartInterpretationMemo]:
        if self.clients.get(client_id) is None:
            raise ClientNotFoundError("Client not found")
        if self.clients.get_chart(client_id) is None:
            raise ChartNotFoundError("Natal chart has not been calculated")
        return self.clients.list_chart_memos(client_id)


@dataclass(slots=True)
class UpdateChartInterpretationMemos:
    clients: ClientRepository

    def execute(
        self, client_id: int, updates: list[tuple[str, str]]
    ) -> list[ChartInterpretationMemo]:
        if self.clients.get(client_id) is None:
            raise ClientNotFoundError("Client not found")
        chart = self.clients.get_chart(client_id)
        if chart is None or chart.id is None:
            raise ChartNotFoundError("Natal chart has not been calculated")

        seen: set[str] = set()
        memos: list[ChartInterpretationMemo] = []
        for planet, content in updates:
            if planet not in SUPPORTED_MEMO_POINTS:
                raise ValueError(f"Unsupported memo point: {planet}")
            if planet in seen:
                raise ValueError(f"Duplicate memo point: {planet}")
            seen.add(planet)
            memos.append(ChartInterpretationMemo(
                chart_id=chart.id, planet=planet, content=content.strip()
            ))
        return self.clients.upsert_chart_memos(client_id, memos)


@dataclass(slots=True)
class ExportNatalChartSummary:
    clients: ClientRepository
    renderer: ChartSummaryRenderer

    def execute(self, client_id: int) -> ChartSummary:
        client = self.clients.get(client_id)
        if client is None:
            raise ClientNotFoundError("Client not found")
        chart = self.clients.get_chart(client_id)
        if chart is None:
            raise ChartNotFoundError("Natal chart has not been calculated")
        return self.renderer.render(client, chart)


@dataclass(slots=True)
class CalculateLillyScore:
    clients: ClientRepository
    calculator: LillyScoreCalculator

    def execute(self, client_id: int) -> LillyScoreResult:
        if self.clients.get(client_id) is None:
            raise ClientNotFoundError("Client not found")
        chart = self.clients.get_chart(client_id)
        if chart is None:
            raise ChartNotFoundError("Natal chart has not been calculated")
        try:
            return self.calculator.calculate(chart)
        except ValueError as exc:
            raise LillyScoreCalculationError(str(exc)) from exc
