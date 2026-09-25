"""Markdown adapter for portable, human- and AI-readable chart summaries."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from app.domain.entities import ChartSummary, Client, NatalChart


SIGN_LABELS = {
    "Ari": "牡羊座", "Tau": "牡牛座", "Gem": "双子座", "Can": "蟹座",
    "Leo": "獅子座", "Vir": "乙女座", "Lib": "天秤座", "Sco": "蠍座",
    "Sag": "射手座", "Cap": "山羊座", "Aqu": "水瓶座", "Pis": "魚座",
}
POINT_LABELS = {
    "Sun": "太陽", "Moon": "月", "Mercury": "水星", "Venus": "金星",
    "Mars": "火星", "Jupiter": "木星", "Saturn": "土星", "Uranus": "天王星",
    "Neptune": "海王星", "Pluto": "冥王星", "Chiron": "キロン",
    "True_North_Lunar_Node": "ドラゴンヘッド", "True_South_Lunar_Node": "ドラゴンテイル",
    "Mean_Lilith": "リリス", "Ascendant": "ASC", "Medium_Coeli": "MC",
    "Descendant": "DSC", "Imum_Coeli": "IC",
}
HOUSE_LABELS = {
    "First_House": "第1ハウス", "Second_House": "第2ハウス", "Third_House": "第3ハウス",
    "Fourth_House": "第4ハウス", "Fifth_House": "第5ハウス", "Sixth_House": "第6ハウス",
    "Seventh_House": "第7ハウス", "Eighth_House": "第8ハウス", "Ninth_House": "第9ハウス",
    "Tenth_House": "第10ハウス", "Eleventh_House": "第11ハウス", "Twelfth_House": "第12ハウス",
}
ASPECT_LABELS = {
    "conjunction": "コンジャンクション", "opposition": "オポジション", "trine": "トライン",
    "square": "スクエア", "sextile": "セクスタイル", "quintile": "クインタイル",
    "quincunx": "クインカンクス", "semisextile": "セミセクスタイル",
    "semisquare": "セミスクエア", "sesquiquadrate": "セスキコードレイト",
}
DEFAULT_POINT_ORDER = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus",
    "Neptune", "Pluto", "Chiron", "True_North_Lunar_Node", "True_South_Lunar_Node",
    "Mean_Lilith", "Ascendant", "Medium_Coeli", "Descendant", "Imum_Coeli",
]
HOUSE_ORDER = list(HOUSE_LABELS)


def format_dms(value: float | int | Decimal) -> str:
    """Round a zodiac degree to the nearest arcsecond."""

    total_seconds = int(
        (Decimal(str(value)) * Decimal(3600)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )
    degrees, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{degrees}°{minutes:02d}′{seconds:02d}″"


def _label(mapping: dict[str, str], value: Any) -> str:
    text = str(value or "—")
    return mapping.get(text, text.replace("_", " "))


def _cell(value: Any) -> str:
    return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")


class MarkdownChartSummaryRenderer:
    def render(self, client: Client, chart: NatalChart) -> ChartSummary:
        calculation = chart.calculation
        subject = calculation.get("subject") or {}
        points = {
            value.get("name"): value
            for value in subject.values()
            if isinstance(value, dict) and value.get("point_type") == "AstrologicalPoint"
        }
        active_points = calculation.get("active_points") or subject.get("active_points") or DEFAULT_POINT_ORDER
        point_order = [name for name in active_points if name in points]
        point_order.extend(name for name in DEFAULT_POINT_ORDER if name in points and name not in point_order)

        lines = [
            f"# {_cell(client.name)} — ネイタルチャート情報",
            "",
            "## 出生情報",
            "",
            f"- 生年月日: {client.birth_date.isoformat()}",
            f"- 出生時刻: {client.birth_time.isoformat() if client.birth_time else '不明'}",
            f"- 出生地: {_cell(client.birth_place)}",
            f"- 緯度・経度: {client.birth_latitude}, {client.birth_longitude}",
            f"- タイムゾーン: {_cell(client.birth_timezone)}",
            f"- チャート種別: {_cell(calculation.get('chart_type', 'Natal'))}",
            f"- 黄道方式: {_cell(subject.get('zodiac_type'))}",
            f"- ハウスシステム: {_cell(subject.get('houses_system_name'))}",
            "",
            "## 天体・感受点",
            "",
            "| 天体・感受点 | サイン | 度数 | 在室ハウス | 状態 |",
            "|---|---|---:|---|---|",
        ]
        for name in point_order:
            point = points[name]
            state = "逆行" if point.get("retrograde") else "順行"
            if name in {"Ascendant", "Medium_Coeli", "Descendant", "Imum_Coeli"}:
                state = "—"
            lines.append(
                f"| {_cell(_label(POINT_LABELS, name))} | {_cell(_label(SIGN_LABELS, point.get('sign')))} "
                f"| {format_dms(point.get('position', 0))} | {_cell(_label(HOUSE_LABELS, point.get('house')))} | {state} |"
            )

        lines.extend([
            "", "## ハウスカスプ", "",
            "| ハウス | サイン | 度数 |", "|---|---|---:|",
        ])
        subject_points = {
            value.get("name"): value
            for value in subject.values()
            if isinstance(value, dict) and value.get("point_type") == "House"
        }
        for name in HOUSE_ORDER:
            if point := subject_points.get(name):
                lines.append(
                    f"| {HOUSE_LABELS[name]} | {_cell(_label(SIGN_LABELS, point.get('sign')))} "
                    f"| {format_dms(point.get('position', 0))} |"
                )

        point_names = set(point_order)
        aspects = [
            aspect for aspect in calculation.get("aspects", [])
            if aspect.get("p1_name") in point_names and aspect.get("p2_name") in point_names
        ]
        aspects.sort(key=lambda item: float(item.get("orbit", 0)))
        lines.extend([
            "", "## アスペクト", "",
            "| 天体・感受点1 | アスペクト | 天体・感受点2 | オーブ | 状態 |",
            "|---|---|---|---:|---|",
        ])
        for aspect in aspects:
            movement = "接近" if aspect.get("aspect_movement") == "Applying" else "分離"
            lines.append(
                f"| {_cell(_label(POINT_LABELS, aspect.get('p1_name')))} "
                f"| {_cell(_label(ASPECT_LABELS, aspect.get('aspect')))} "
                f"| {_cell(_label(POINT_LABELS, aspect.get('p2_name')))} "
                f"| {format_dms(aspect.get('orbit', 0))} | {movement} |"
            )

        lines.extend([
            "", "---", "",
            f"計算エンジン: Kerykeion {chart.calculation_version}", "",
        ])
        return ChartSummary(
            content="\n".join(lines), media_type="text/markdown; charset=utf-8", file_extension="md"
        )
