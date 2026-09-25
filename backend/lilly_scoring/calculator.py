"""Pure Lilly scoring rules with no ephemeris or framework dependency."""

from math import isclose

from .dignity_tables import DETRIMENT, DOMICILE, ELEMENT, EXALTATION, FACES, FALL, SIGNS, TERMS, TRIPLICITY
from .models import CLASSICAL_PLANETS, ChartInput, LillyScoreResult, PlanetInput, PlanetName as P, PlanetScore, ScoreItem, ScoreSection


HOUSE_POINTS = {1: 5, 2: 3, 3: 1, 4: 4, 5: 3, 6: -2, 7: 4, 8: -2, 9: 2, 10: 5, 11: 4, 12: -5}
AVERAGE_MOTION = {P.SATURN: .033611, P.JUPITER: .083056, P.MARS: .524167, P.SUN: .985556, P.VENUS: .985556, P.MERCURY: .985556, P.MOON: 13.176667}
PLANET_LABELS = {P.SUN: "太陽", P.MOON: "月", P.MERCURY: "水星", P.VENUS: "金星", P.MARS: "火星", P.JUPITER: "木星", P.SATURN: "土星"}
STAR_RULES = {"Regulus": (6, 1.0, "レグルス"), "Spica": (5, 1.0, "スピカ"), "Algol": (-5, 5.0, "アルゴル")}


def _normalize(value: float) -> float:
    return value % 360.0


def _distance(a: float, b: float) -> float:
    difference = abs(_normalize(a) - _normalize(b))
    return min(difference, 360.0 - difference)


def _sign(longitude: float) -> str:
    return SIGNS[int(_normalize(longitude) // 30)]


def _degree(longitude: float) -> float:
    return _normalize(longitude) % 30


def _format_dm(value: float) -> str:
    """Format an angle as degrees and whole arcminutes for display."""

    prefix = "-" if value < 0 else ""
    total_minutes = int(abs(value) * 60 + 1e-9)
    degrees, minutes = divmod(total_minutes, 60)
    return f"{prefix}{degrees}°{minutes:02d}′"


def _format_dms(value: float) -> str:
    """Format daily motion to the nearest arcsecond."""

    prefix = "-" if value < 0 else ""
    total_seconds = int(abs(value) * 3600 + 0.5)
    degrees, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{prefix}{degrees}°{minutes:02d}′{seconds:02d}″"


def _item(code: str, label: str, points: int, description: str, related: str | None = None, status: str = "awarded") -> ScoreItem:
    return ScoreItem(code, label, points, description, status, related)


def _validate(chart: ChartInput) -> dict[P, PlanetInput]:
    planets = {planet.name: planet for planet in chart.planets}
    missing = set(CLASSICAL_PLANETS) - set(planets)
    if missing:
        raise ValueError(f"Missing classical planets: {', '.join(sorted(item.value for item in missing))}")
    if len(planets) != len(chart.planets):
        raise ValueError("Planet names must be unique")
    if set(chart.house_cusps) != set(range(1, 13)):
        raise ValueError("All twelve house cusps are required")
    for planet in planets.values():
        if planet.house not in range(1, 13):
            raise ValueError(f"Invalid house for {planet.name.value}")
    return planets


def _essential(planet: PlanetInput, planets: dict[P, PlanetInput], sect: str) -> ScoreSection:
    sign, degree = _sign(planet.longitude), _degree(planet.longitude)
    items: list[ScoreItem] = []
    positive_dignity = False
    checks = ((DOMICILE, planet.name, "domicile", "ドミサイル", 5), (EXALTATION, planet.name, "exaltation", "エグザルテーション", 4), (DETRIMENT, planet.name, "detriment", "デトリメント", -5), (FALL, planet.name, "fall", "フォール", -4))
    for table, expected, code, label, points in checks:
        if table.get(sign) == expected:
            items.append(_item(code, label, points, f"{sign}全域で成立"))
            positive_dignity |= points > 0

    ruler = TRIPLICITY[ELEMENT[sign]][sect]
    if ruler == planet.name:
        items.append(_item("triplicity", "トリプリシティ", 3, f"{sect}セクトの{ELEMENT[sign]}エレメント支配"))
        positive_dignity = True
    term_ruler = next(ruler for end, ruler in TERMS[sign] if degree < end)
    if term_ruler == planet.name:
        items.append(_item("term", "ターム", 2, f"{sign} {_format_dm(degree)}のターム支配"))
        positive_dignity = True
    face_ruler = FACES[sign][min(int(degree // 10), 2)]
    if face_ruler == planet.name:
        items.append(_item("face", "フェイス", 1, f"{sign} {_format_dm(degree)}のフェイス支配"))
        positive_dignity = True
    if not positive_dignity:
        items.append(_item("peregrine", "ペレグリン", -5, "加点となる基本品位なし"))

    for other in planets.values():
        if other.name == planet.name:
            continue
        other_sign = _sign(other.longitude)
        if DOMICILE.get(sign) == other.name and DOMICILE.get(other_sign) == planet.name:
            items.append(_item("mutual_reception_domicile", "ミューチュアルレセプション（ドミサイル）", 5, f"{PLANET_LABELS[other.name]}とドミサイルを交換", other.name.value))
        if EXALTATION.get(sign) == other.name and EXALTATION.get(other_sign) == planet.name:
            items.append(_item("mutual_reception_exaltation", "ミューチュアルレセプション（エグザルテーション）", 4, f"{PLANET_LABELS[other.name]}とエグザルテーションを交換", other.name.value))
    return ScoreSection(sum(item.points for item in items), tuple(items))


def _effective_house(planet: PlanetInput, cusps: dict[int, float]) -> tuple[int, float]:
    next_house = planet.house % 12 + 1
    distance_to_next = (_normalize(cusps[next_house]) - _normalize(planet.longitude)) % 360
    return (next_house, distance_to_next) if distance_to_next <= 5 else (planet.house, distance_to_next)


def _aspect_item(target: PlanetInput, other: PlanetInput, rules: tuple[tuple[float, int, str], ...], prefix: str) -> ScoreItem | None:
    separation = _distance(target.longitude, other.longitude)
    for angle, points, label in rules:
        if abs(separation - angle) <= 1:
            return _item(f"{prefix}_{int(angle)}", label, points, f"{PLANET_LABELS[other.name]}とパータイル（オーブ {_format_dm(abs(separation-angle))}）", other.name.value)
    return None


def _between_on_short_arc(value: float, a: float, b: float) -> bool:
    forward = (_normalize(b) - _normalize(a)) % 360
    if forward <= 180:
        return (_normalize(value) - _normalize(a)) % 360 <= forward
    reverse = (_normalize(a) - _normalize(b)) % 360
    return (_normalize(value) - _normalize(b)) % 360 <= reverse


def _accidental(planet: PlanetInput, planets: dict[P, PlanetInput], chart: ChartInput) -> ScoreSection:
    items: list[ScoreItem] = []
    house, cusp_distance = _effective_house(planet, chart.house_cusps)
    moved = house != planet.house
    house_description = "在室ハウス配点"
    if moved:
        house_description += f"（5度前ルール適用、カスプまで {_format_dm(cusp_distance)}）"
    items.append(_item("house", f"第{house}ハウス", HOUSE_POINTS[house], house_description))

    if planet.name not in {P.SUN, P.MOON}:
        points = -5 if planet.retrograde else 4
        items.append(_item("retrograde" if planet.retrograde else "direct", "逆行" if planet.retrograde else "順行", points, "運行方向による配点"))

    motion, average = abs(planet.daily_motion), AVERAGE_MOTION[planet.name]
    if isclose(motion, average, rel_tol=0, abs_tol=1e-9):
        items.append(_item("average_speed", "平均速度と同じ", 0, f"日運動 {_format_dms(motion)}", status="neutral"))
    elif motion > average:
        items.append(_item("fast", "平均より速い", 2, f"日運動 {_format_dms(motion)} > 平均 {_format_dms(average)}"))
    else:
        items.append(_item("slow", "平均より遅い", -2, f"日運動 {_format_dms(motion)} < 平均 {_format_dms(average)}"))

    sun = planets[P.SUN]
    if planet.name != P.SUN:
        separation = _distance(planet.longitude, sun.longitude)
        planet_from_sun = (_normalize(planet.longitude) - _normalize(sun.longitude)) % 360
        if separation > 1:
            # At exactly 180 degrees the specification gives oriental priority.
            oriental = planet_from_sun >= 180
            outer = planet.name in {P.MARS, P.JUPITER, P.SATURN}
            points = (2 if oriental else -2) if outer else (-2 if oriental else 2)
            label = "オリエンタル" if oriental else "オキシデンタル"
            items.append(_item("oriental" if oriental else "occidental", label, points, f"太陽から天体への黄経差 {_format_dm(planet_from_sun)}"))

        same_sign = _sign(planet.longitude) == _sign(sun.longitude)
        if separation <= 17 / 60:
            items.append(_item("cazimi", "カジミ", 5, f"太陽との離角 {_format_dm(separation)}"))
        elif separation <= 8.5 and same_sign:
            items.append(_item("combust", "コンバスト", -5, f"太陽との離角 {_format_dm(separation)}、同一サイン"))
        elif separation <= 17:
            description = f"太陽との離角 {_format_dm(separation)}"
            if separation <= 8.5 and not same_sign:
                description += "。太陽とはサイン違いのためコンバスト不成立"
            items.append(_item("under_sunbeams", "アンダー・ザ・サンビーム", -4, description))
        else:
            items.append(_item("free_from_sunbeams", "太陽光線外", 5, f"太陽との離角 {_format_dm(separation)}"))

    for longitude, code, label, points in ((chart.north_node_longitude, "north_node_conjunction", "ドラゴンヘッド合", 4), (chart.south_node_longitude, "south_node_conjunction", "ドラゴンテイル合", -4)):
        if longitude is not None and _distance(planet.longitude, longitude) <= 1:
            items.append(_item(code, label, points, f"コンジャンクション、オーブ {_format_dm(_distance(planet.longitude, longitude))}"))

    benefic_rules = ((0, 5, "ベネフィックとのコンジャンクション"), (120, 4, "ベネフィックとのトライン"), (60, 3, "ベネフィックとのセクスタイル"))
    malefic_rules = ((0, -5, "マレフィックとのコンジャンクション"), (180, -4, "マレフィックとのオポジション"), (90, -3, "マレフィックとのスクエア"))
    for name in (P.JUPITER, P.VENUS):
        if planet.name != name and (result := _aspect_item(planet, planets[name], benefic_rules, "benefic")):
            items.append(result)
    for name in (P.MARS, P.SATURN):
        if planet.name != name and (result := _aspect_item(planet, planets[name], malefic_rules, "malefic")):
            items.append(result)

    mars, saturn = planets[P.MARS], planets[P.SATURN]
    if planet.name not in {P.MARS, P.SATURN} and _distance(mars.longitude, saturn.longitude) <= 6 and _between_on_short_arc(planet.longitude, mars.longitude, saturn.longitude):
        items.append(_item("besieged", "火星・土星に挟まれる", -5, f"火星と土星の最短角距離 {_format_dm(_distance(mars.longitude, saturn.longitude))}"))

    missing_stars = [name for name in STAR_RULES if chart.fixed_stars.get(name) is None]
    if missing_stars:
        items.append(_item("fixed_stars_unavailable", "恒星アスペクト", 0, f"採点不能: {', '.join(missing_stars)}の黄経が未定義", status="unavailable"))
    else:
        for name, (points, orb, label) in STAR_RULES.items():
            distance = _distance(planet.longitude, float(chart.fixed_stars[name]))
            if distance <= orb:
                items.append(_item(f"fixed_star_{name.lower()}", f"{label}とのコンジャンクション", points, f"オーブ {_format_dm(distance)}", name))
    return ScoreSection(sum(item.points for item in items), tuple(items))


def score_chart(chart: ChartInput) -> LillyScoreResult:
    """Score a complete classical chart using the supplied chart facts only."""

    planets = _validate(chart)
    sect = "night" if planets[P.SUN].house <= 6 else "day"
    scores = tuple(
        PlanetScore(planet.name, _essential(planet, planets, sect), _accidental(planet, planets, chart))
        for planet in chart.planets
    )
    warnings = ()
    if any(chart.fixed_stars.get(name) is None for name in STAR_RULES):
        warnings = ("恒星（レグルス・スピカ・アルゴル）の黄経不足により、恒星アスペクトは採点不能です。",)
    return LillyScoreResult(sect, scores, warnings)
