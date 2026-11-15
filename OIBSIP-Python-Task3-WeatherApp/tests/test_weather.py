"""Tests for the weather logic with the network mocked. Run from the project root:
    python -m unittest discover tests
"""
import os
import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather import api  # noqa: E402
from weather.config import load_env  # noqa: E402
from weather.units import c_to_f, format_temp, format_wind, ms_to_mph  # noqa: E402

CURRENT_JSON = {
    "name": "Bengaluru", "sys": {"country": "IN"}, "coord": {"lat": 12.97, "lon": 77.59},
    "main": {"temp": 24.4, "feels_like": 25.1, "humidity": 70},
    "weather": [{"description": "partly cloudy", "icon": "02d"}], "wind": {"speed": 3.2},
}


def fake_response(status=200, payload=None):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = payload if payload is not None else {}
    return resp


class InputTests(unittest.TestCase):
    def test_empty_rejected(self):
        for text in ("", "   ", None):
            with self.assertRaises(api.WeatherError):
                api.validate_query(text)

    def test_city_vs_zip(self):
        self.assertEqual(api.build_params("Mumbai"), ({"q": "Mumbai"}, False))
        self.assertEqual(api.build_params("94040"), ({"zip": "94040,US"}, True))
        self.assertEqual(api.build_params("560001,IN"), ({"zip": "560001,IN"}, True))


class UnitTests(unittest.TestCase):
    def test_conversions(self):
        self.assertEqual(c_to_f(0), 32)
        self.assertEqual(c_to_f(100), 212)
        self.assertAlmostEqual(ms_to_mph(10), 22.3694, places=3)

    def test_formatting(self):
        self.assertEqual(format_temp(25, "C"), "25°C")
        self.assertEqual(format_temp(25, "F"), "77°F")
        self.assertEqual(format_wind(10, "C"), "10.0 m/s")
        self.assertEqual(format_wind(10, "F"), "22.4 mph")


@patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test-key"})
class HttpErrorTests(unittest.TestCase):
    def test_success_parses(self):
        with patch("weather.api.requests.get", return_value=fake_response(200, CURRENT_JSON)):
            current = api.get_current("Bengaluru")
        self.assertEqual((current.city, current.country, current.humidity), ("Bengaluru", "IN", 70))
        self.assertEqual(current.description, "Partly Cloudy")

    def test_status_codes_map_to_messages(self):
        expectations = {401: "Invalid API key", 404: "not found", 429: "Too many requests", 500: "error (500)"}
        for status, text in expectations.items():
            with patch("weather.api.requests.get", return_value=fake_response(status)):
                with self.assertRaises(api.WeatherError) as ctx:
                    api.get_current("Nowhere")
            self.assertIn(text, str(ctx.exception), msg=status)

    def test_timeout_and_network(self):
        with patch("weather.api.requests.get", side_effect=requests.exceptions.Timeout):
            with self.assertRaisesRegex(api.WeatherError, "timed out"):
                api.get_current("Pune")
        with patch("weather.api.requests.get", side_effect=requests.exceptions.ConnectionError):
            with self.assertRaisesRegex(api.WeatherError, "Network problem"):
                api.get_current("Pune")

    def test_zip_not_found_hint(self):
        with patch("weather.api.requests.get", return_value=fake_response(404)):
            with self.assertRaisesRegex(api.WeatherError, "country code"):
                api.get_current("560001")

    def test_bad_payload(self):
        with patch("weather.api.requests.get", return_value=fake_response(200, {"unexpected": 1})):
            with self.assertRaises(api.WeatherError):
                api.get_current("Pune")

    def test_missing_key(self):
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": ""}):
            with self.assertRaisesRegex(api.WeatherError, "API key"):
                api.get_current("Pune")


class ForecastTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 15, 10, 0, tzinfo=timezone.utc).timestamp()
        self.data = {
            "city": {"timezone": 0},
            "list": [
                {"dt": int(self.now + 3 * 3600 * (i + 1)),
                 "main": {"temp": 10 + i % 8, "temp_min": 9 + i % 8, "temp_max": 11 + i % 8},
                 "weather": [{"description": "clear sky", "icon": "01n"}]}
                for i in range(40)
            ],
        }

    def test_hourly_covers_next_six_hours(self):
        hourly, _ = api.parse_forecast(self.data, now_ts=self.now)
        self.assertEqual(len(hourly), 2)

    def test_five_days_and_min_max(self):
        _, daily = api.parse_forecast(self.data, now_ts=self.now)
        self.assertEqual(len(daily), 5)
        self.assertTrue(all(d.min_c <= d.max_c for d in daily))
        self.assertTrue(all(d.icon.endswith("d") for d in daily))
        self.assertTrue(all(d.date > datetime.fromtimestamp(self.now, tz=timezone.utc).date() for d in daily))

    def test_bad_forecast(self):
        with self.assertRaises(api.WeatherError):
            api.parse_forecast({"nope": 1}, now_ts=self.now)


class LocationAndConfigTests(unittest.TestCase):
    def test_locate_by_ip(self):
        with patch("weather.api.requests.get", return_value=fake_response(200, {"city": "Kolar"})):
            self.assertEqual(api.locate_by_ip(), "Kolar")
        with patch("weather.api.requests.get", return_value=fake_response(200, {})):
            with self.assertRaises(api.WeatherError):
                api.locate_by_ip()
        with patch("weather.api.requests.get", side_effect=requests.exceptions.ConnectionError):
            with self.assertRaises(api.WeatherError):
                api.locate_by_ip()

    def test_load_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text('# comment\nTEST_WEATHER_KEY="abc123"\n\nBAD LINE\n', encoding="utf-8")
            os.environ.pop("TEST_WEATHER_KEY", None)
            load_env(path)
            self.assertEqual(os.environ.get("TEST_WEATHER_KEY"), "abc123")
            os.environ.pop("TEST_WEATHER_KEY", None)


if __name__ == "__main__":
    unittest.main()
