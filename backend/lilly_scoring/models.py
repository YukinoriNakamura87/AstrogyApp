"""Public input/output types for the standalone Lilly scoring library."""

from dataclasses import dataclass, field
from enum import StrEnum


class PlanetName(StrEnum):
    SUN = "Sun"
    MOON = "Moon"
    MERCURY = "Mercury"
    VENUS = "Venus"
    MARS = "Mars"
    JUPITER = "Jupiter"
    SATURN = "Saturn"


CLASSICAL_PLANETS = tuple(PlanetName)


@dataclass(frozen=True, slots=True)
class PlanetInput:
    name: PlanetName
    longitude: float
    house: int
    retrograde: bool
    daily_motion: float


@dataclass(frozen=True, slots=True)
class ChartInput:
    planets: tuple[PlanetInput, ...]
    house_cusps: dict[int, float]
    north_node_longitude: float | None = None
    south_node_longitude: float | None = None
    fixed_stars: dict[str, float | None] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ScoreItem:
    code: str
    label: str
    points: int
    description: str
    status: str = "awarded"
    related_body: str | None = None


@dataclass(frozen=True, slots=True)
class ScoreSection:
    total: int
    items: tuple[ScoreItem, ...]


@dataclass(frozen=True, slots=True)
class PlanetScore:
    planet: PlanetName
    essential: ScoreSection
    accidental: ScoreSection

    @property
    def total(self) -> int:
        return self.essential.total + self.accidental.total


@dataclass(frozen=True, slots=True)
class LillyScoreResult:
    sect: str
    planets: tuple[PlanetScore, ...]
    warnings: tuple[str, ...] = ()

    @property
    def essential_total(self) -> int:
        return sum(item.essential.total for item in self.planets)

    @property
    def accidental_total(self) -> int:
        return sum(item.accidental.total for item in self.planets)

    @property
    def grand_total(self) -> int:
        return self.essential_total + self.accidental_total
