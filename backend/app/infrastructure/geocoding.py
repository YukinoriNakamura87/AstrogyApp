"""Open-Meteo adapter for resolving birth places."""

import os
from decimal import Decimal, InvalidOperation

import httpx

from app.domain.entities import BirthPlaceCandidate
from app.domain.services import GeocodingProviderError


class OpenMeteoGeocodingProvider:
    def __init__(self, base_url: str | None = None, timeout_seconds: float = 5.0):
        self.base_url = base_url or os.getenv(
            "OPEN_METEO_GEOCODING_BASE_URL",
            "https://geocoding-api.open-meteo.com/v1",
        )
        self.timeout_seconds = timeout_seconds

    def search(self, query: str, *, limit: int = 8) -> list[BirthPlaceCandidate]:
        try:
            response = httpx.get(
                f"{self.base_url.rstrip('/')}/search",
                params={"name": query, "count": limit, "language": "ja", "format": "json"},
                timeout=self.timeout_seconds,
                headers={"User-Agent": "Astrolabe/0.1 (birth-place lookup)"},
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise GeocodingProviderError("Open-Meteo request failed") from exc

        candidates: list[BirthPlaceCandidate] = []
        for item in payload.get("results", []):
            try:
                latitude = Decimal(str(item["latitude"]))
                longitude = Decimal(str(item["longitude"]))
                timezone = str(item["timezone"])
                name = str(item["name"])
            except (KeyError, InvalidOperation, TypeError, ValueError):
                continue
            candidates.append(
                BirthPlaceCandidate(
                    provider_id=str(item.get("id", f"{latitude},{longitude}")),
                    name=name,
                    admin1=item.get("admin1"),
                    admin2=item.get("admin2"),
                    country=str(item.get("country", "")),
                    country_code=str(item.get("country_code", "")),
                    latitude=latitude,
                    longitude=longitude,
                    timezone=timezone,
                )
            )
        return candidates
