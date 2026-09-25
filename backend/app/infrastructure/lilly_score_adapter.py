"""Anti-corruption adapter from cached Kerykeion JSON to the standalone library."""

from typing import Any

from app.domain.entities import NatalChart
from lilly_scoring import ChartInput, PlanetInput, PlanetName, score_chart
from lilly_scoring.models import LillyScoreResult


HOUSE_NUMBERS = {
    "First_House": 1, "Second_House": 2, "Third_House": 3, "Fourth_House": 4,
    "Fifth_House": 5, "Sixth_House": 6, "Seventh_House": 7, "Eighth_House": 8,
    "Ninth_House": 9, "Tenth_House": 10, "Eleventh_House": 11, "Twelfth_House": 12,
}


def _points_by_name(subject: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        value["name"]: value
        for value in subject.values()
        if isinstance(value, dict) and value.get("name") and value.get("abs_pos") is not None
    }


class CachedChartLillyScoreCalculator:
    def calculate(self, chart: NatalChart) -> LillyScoreResult:
        subject = chart.calculation.get("subject") or {}
        points = _points_by_name(subject)
        planets = []
        for name in PlanetName:
            raw = points.get(name.value)
            if raw is None:
                raise ValueError(f"採点に必要な天体がありません: {name.value}")
            house = HOUSE_NUMBERS.get(raw.get("house"))
            if house is None:
                raise ValueError(f"在室ハウスが不明です: {name.value}")
            planets.append(PlanetInput(
                name=name,
                longitude=float(raw["abs_pos"]),
                house=house,
                retrograde=bool(raw.get("retrograde")),
                daily_motion=float(raw.get("speed", 0)),
            ))

        house_cusps = {}
        for house_name, number in HOUSE_NUMBERS.items():
            raw = points.get(house_name)
            if raw is None:
                raise ValueError(f"採点に必要なハウスカスプがありません: {house_name}")
            house_cusps[number] = float(raw["abs_pos"])

        def longitude(name: str) -> float | None:
            point = points.get(name)
            return float(point["abs_pos"]) if point else None

        source = ChartInput(
            planets=tuple(planets),
            house_cusps=house_cusps,
            north_node_longitude=longitude("True_North_Lunar_Node"),
            south_node_longitude=longitude("True_South_Lunar_Node"),
            fixed_stars={
                "Regulus": longitude("Regulus"),
                "Spica": longitude("Spica"),
                "Algol": longitude("Algol"),
            },
        )
        return score_chart(source)
