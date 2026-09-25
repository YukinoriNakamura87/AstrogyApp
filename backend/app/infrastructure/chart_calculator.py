"""Kerykeion adapter implementing the natal-chart calculator port."""

from importlib.metadata import version

from kerykeion import AstrologicalSubjectFactory, ChartDataFactory
from kerykeion.settings.config_constants import DEFAULT_ACTIVE_POINTS

from app.domain.entities import Client, NatalChart


# Extra facts retained for future interpretation features. These are calculated on
# the subject, but deliberately excluded from ChartDataFactory's active points so
# they do not alter the existing aspects or element/quality distributions.
FIXED_STAR_POINTS = (
    "Regulus", "Spica", "Algol", "Aldebaran", "Antares", "Sirius",
    "Fomalhaut", "Betelgeuse", "Canopus", "Procyon", "Arcturus", "Pollux",
    "Deneb", "Altair", "Rigel", "Achernar", "Capella", "Vega", "Alcyone",
    "Alphecca", "Algorab", "Deneb_Algedi", "Alkaid",
)
SUPPLEMENTARY_POINTS = (
    "Mean_North_Lunar_Node", "Mean_South_Lunar_Node", "True_Lilith",
    "Ceres", "Pallas", "Juno", "Vesta", "Vertex", "Anti_Vertex",
    "Pars_Fortunae", "Pars_Spiritus", "Pars_Amoris", "Pars_Fidei",
)
SUBJECT_ACTIVE_POINTS = tuple(dict.fromkeys([
    *DEFAULT_ACTIVE_POINTS, *FIXED_STAR_POINTS, *SUPPLEMENTARY_POINTS,
]))


class KerykeionNatalChartCalculator:
    def calculate(self, client: Client) -> NatalChart:
        if client.id is None or client.birth_time is None:
            raise ValueError("A persisted client with birth time is required")
        subject = AstrologicalSubjectFactory.from_birth_data(
            name=client.name, year=client.birth_date.year,
            month=client.birth_date.month, day=client.birth_date.day,
            hour=client.birth_time.hour, minute=client.birth_time.minute,
            seconds=client.birth_time.second, city=client.birth_place,
            lng=float(client.birth_longitude), lat=float(client.birth_latitude),
            tz_str=client.birth_timezone, online=False,
            active_points=list(SUBJECT_ACTIVE_POINTS),
        )
        result = ChartDataFactory.create_natal_chart_data(
            subject,
            # Keep chart-derived aspects and distributions backward compatible.
            active_points=list(DEFAULT_ACTIVE_POINTS),
        )
        return NatalChart(
            client_id=client.id,
            calculation=result.model_dump(mode="json"),
            calculation_version=version("kerykeion"),
        )
