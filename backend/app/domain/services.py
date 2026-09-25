"""Ports for domain services supplied by external libraries."""

from typing import Protocol

from app.domain.entities import BirthPlaceCandidate, ChartSummary, Client, NatalChart
from lilly_scoring.models import LillyScoreResult


class NatalChartCalculator(Protocol):
    def calculate(self, client: Client) -> NatalChart: ...


class ChartSummaryRenderer(Protocol):
    def render(self, client: Client, chart: NatalChart) -> ChartSummary: ...


class LillyScoreCalculator(Protocol):
    def calculate(self, chart: NatalChart) -> LillyScoreResult: ...


class GeocodingProvider(Protocol):
    def search(self, query: str, *, limit: int = 8) -> list[BirthPlaceCandidate]: ...


class GeocodingProviderError(Exception):
    """Raised when an external place provider cannot serve a search."""
