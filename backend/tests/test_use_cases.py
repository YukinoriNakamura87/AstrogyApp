from datetime import date, time
from decimal import Decimal
from unittest import TestCase

from app.application.use_cases import ChartCalculationError, ChartNotFoundError, ClientNotFoundError, ExportNatalChartSummary, GetClientProfile, GetDashboard, GetOrCreateNatalChart, ListClients, SearchBirthPlaces
from app.domain.entities import BirthPlaceCandidate, ChartSignature, Client, ClientOverview, NatalChart
from app.infrastructure.markdown_chart_summary import MarkdownChartSummaryRenderer, format_dms


def client(client_id: int = 1, birth_time: time | None = time(12, 0)) -> Client:
    return Client(
        id=client_id, name="Yuki", birth_date=date(1992, 8, 7),
        birth_time=birth_time, birth_place="滋賀県守山市",
        birth_latitude=Decimal("35.0589"), birth_longitude=Decimal("135.9944"),
        birth_timezone="Asia/Tokyo",
    )


class FakeRepository:
    def __init__(self, item: Client, chart: NatalChart | None = None):
        self.item = item
        self.chart = chart
        self.saved = False

    def get(self, client_id: int, *, for_update: bool = False):
        return self.item if client_id == self.item.id else None

    def get_chart(self, client_id: int):
        return self.chart

    def save_chart(self, chart: NatalChart):
        self.saved = True
        self.chart = chart
        return chart

    def list_overviews(self, search=None):
        return [ClientOverview(self.item, self.chart is not None, ChartSignature("Leo", "Sag", "Sco"))]

    def count(self): return 1
    def count_with_chart(self): return int(self.chart is not None)
    def rollback(self): pass


class FakeCalculator:
    def __init__(self): self.called = False

    def calculate(self, item: Client):
        self.called = True
        return NatalChart(client_id=item.id or 0, calculation={"subject": {}}, calculation_version="test")


class FakeGeocodingProvider:
    def __init__(self): self.query = None

    def search(self, query: str, *, limit: int = 8):
        self.query = query
        return [BirthPlaceCandidate(
            provider_id="1", name="守山市", admin1="滋賀県", admin2="守山市",
            country="日本", country_code="JP", latitude=Decimal("35.0589"),
            longitude=Decimal("135.9944"), timezone="Asia/Tokyo",
        )]


class UseCaseTests(TestCase):
    def test_client_profile_contains_cached_chart(self):
        cached = NatalChart(client_id=1, calculation={}, calculation_version="cached")
        profile = GetClientProfile(FakeRepository(client(), cached)).execute(1)
        self.assertEqual(profile.client.name, "Yuki")
        self.assertIs(profile.chart, cached)

    def test_client_profile_rejects_unknown_client(self):
        with self.assertRaises(ClientNotFoundError):
            GetClientProfile(FakeRepository(client())).execute(999)

    def test_cached_chart_does_not_recalculate(self):
        cached = NatalChart(client_id=1, calculation={}, calculation_version="cached")
        repository, calculator = FakeRepository(client(), cached), FakeCalculator()
        result = GetOrCreateNatalChart(repository, calculator).execute(1)
        self.assertEqual(result.calculation_version, "cached")
        self.assertFalse(calculator.called)

    def test_chart_requires_birth_time(self):
        with self.assertRaises(ChartCalculationError):
            GetOrCreateNatalChart(FakeRepository(client(birth_time=None)), FakeCalculator()).execute(1)

    def test_sign_filter_matches_any_big_three_position(self):
        result = ListClients(FakeRepository(client())).execute(sign="sco")
        self.assertEqual(len(result), 1)
        self.assertEqual(ListClients(FakeRepository(client())).execute(sign="pis"), [])

    def test_dashboard_uses_repository_counts(self):
        result = GetDashboard(FakeRepository(client())).execute()
        self.assertEqual(result["client_count"], 1)
        self.assertEqual(result["session_count"], 0)

    def test_birth_place_search_normalizes_query(self):
        provider = FakeGeocodingProvider()
        result = SearchBirthPlaces(provider).execute("  守山市  ")
        self.assertEqual(provider.query, "守山市")
        self.assertEqual(result[0].display_name, "守山市、滋賀県、日本")

    def test_birth_place_search_rejects_short_query(self):
        with self.assertRaises(ValueError):
            SearchBirthPlaces(FakeGeocodingProvider()).execute("東")

    def test_chart_summary_requires_cached_chart(self):
        with self.assertRaises(ChartNotFoundError):
            ExportNatalChartSummary(
                FakeRepository(client()), MarkdownChartSummaryRenderer()
            ).execute(1)

    def test_markdown_summary_uses_dms_and_house(self):
        cached = NatalChart(
            client_id=1,
            calculation={
                "chart_type": "Natal",
                "active_points": ["Sun"],
                "subject": {
                    "zodiac_type": "Tropical",
                    "houses_system_name": "Placidus",
                    "sun": {
                        "name": "Sun", "point_type": "AstrologicalPoint", "sign": "Leo",
                        "position": 14.3958365, "house": "Ninth_House", "retrograde": False,
                    },
                    "first_house": {
                        "name": "First_House", "point_type": "House", "sign": "Sco",
                        "position": 7.3386551,
                    },
                },
                "aspects": [],
            },
            calculation_version="test",
        )
        summary = ExportNatalChartSummary(
            FakeRepository(client(), cached), MarkdownChartSummaryRenderer()
        ).execute(1)
        self.assertIn("| 太陽 | 獅子座 | 14°23′45″ | 第9ハウス | 順行 |", summary.content)
        self.assertIn("| 第1ハウス | 蠍座 | 7°20′19″ |", summary.content)
        self.assertEqual(format_dms(1.9999), "2°00′00″")
