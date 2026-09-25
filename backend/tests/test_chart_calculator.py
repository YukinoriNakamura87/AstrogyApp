from datetime import date, time
from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch

from app.domain.entities import Client
from app.infrastructure.chart_calculator import (
    FIXED_STAR_POINTS, SUBJECT_ACTIVE_POINTS, SUPPLEMENTARY_POINTS,
    KerykeionNatalChartCalculator,
)
from kerykeion.settings.config_constants import DEFAULT_ACTIVE_POINTS


class _Result:
    def model_dump(self, mode):
        return {"mode": mode}


class ChartCalculatorTests(TestCase):
    @patch("app.infrastructure.chart_calculator.version", return_value="test")
    @patch("app.infrastructure.chart_calculator.ChartDataFactory.create_natal_chart_data", return_value=_Result())
    @patch("app.infrastructure.chart_calculator.AstrologicalSubjectFactory.from_birth_data", return_value=object())
    def test_enrichment_points_are_stored_without_changing_chart_active_points(
        self, create_subject, create_chart, _version,
    ):
        client = Client(
            id=1, name="Yuki", birth_date=date(1992, 8, 7), birth_time=time(12, 30),
            birth_place="Moriyama", birth_latitude=Decimal("35.0589"),
            birth_longitude=Decimal("135.9944"), birth_timezone="Asia/Tokyo",
        )

        result = KerykeionNatalChartCalculator().calculate(client)

        subject_points = create_subject.call_args.kwargs["active_points"]
        chart_points = create_chart.call_args.kwargs["active_points"]
        self.assertTrue(set(FIXED_STAR_POINTS).issubset(subject_points))
        self.assertTrue(set(SUPPLEMENTARY_POINTS).issubset(subject_points))
        self.assertTrue({"Regulus", "Spica", "Algol"}.issubset(subject_points))
        self.assertEqual(chart_points, list(DEFAULT_ACTIVE_POINTS))
        self.assertNotIn("Regulus", chart_points)
        self.assertEqual(result.calculation, {"mode": "json"})
