from unittest import TestCase
from unittest.mock import Mock, patch

from app.infrastructure.geocoding import OpenMeteoGeocodingProvider


class OpenMeteoGeocodingProviderTests(TestCase):
    @patch("app.infrastructure.geocoding.httpx.get")
    def test_maps_open_meteo_result(self, get: Mock):
        response = Mock()
        response.json.return_value = {"results": [{
            "id": 1856560, "name": "守山市", "admin1": "滋賀県",
            "admin2": "守山市", "country": "日本", "country_code": "JP",
            "latitude": 35.05894, "longitude": 135.9944,
            "timezone": "Asia/Tokyo",
        }]}
        get.return_value = response

        result = OpenMeteoGeocodingProvider().search("守山市")

        self.assertEqual(result[0].timezone, "Asia/Tokyo")
        self.assertEqual(str(result[0].latitude), "35.05894")
        get.assert_called_once()
