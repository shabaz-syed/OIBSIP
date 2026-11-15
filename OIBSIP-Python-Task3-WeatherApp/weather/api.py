"""Talks to OpenWeatherMap (current weather + 5-day forecast) and ipinfo.io (location by IP)."""
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import requests

BASE_URL = "https://api.openweathermap.org/data/2.5"
ICON_URL = "https://openweathermap.org/img/wn/{code}@2x.png"
IPINFO_URL = "https://ipinfo.io/json"
TIMEOUT = 8  # seconds


class WeatherError(Exception):
    """An error with a message that is safe to show directly to the user."""


@dataclass
class Current:
    city: str
    country: str
    temp_c: float
    feels_c: float
    humidity: int
    description: str
    wind_ms: float
    icon: str
    lat: float
    lon: float


@dataclass
class HourlyEntry:
    time: datetime
    temp_c: float
    description: str
    icon: str


@dataclass
class DailyEntry:
    date: object
    min_c: float
    max_c: float
    description: str
    icon: str


@dataclass
class Report:
    current: Current
    hourly: list = field(default_factory=list)
    daily: list = field(default_factory=list)

    def icon_codes(self):
        codes = {self.current.icon}
        codes.update(h.icon for h in self.hourly)
        codes.update(d.icon for d in self.daily)
        return codes


# ---------- input handling ----------
def get_api_key():
    key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if not key:
        raise WeatherError("No API key found. Set OPENWEATHER_API_KEY (see the README).")
    return key


def validate_query(text):
    text = (text or "").strip()
    if not text:
        raise WeatherError("Please enter a city name or ZIP code.")
    if len(text) > 80:
        raise WeatherError("That input is too long. Enter a city name or ZIP code.")
    return text


def build_params(query):
    """A ZIP/postal code (optionally with a country, e.g. 560001,IN) or a city name."""
    if re.fullmatch(r"\d{3,10}(,[A-Za-z]{2})?", query):
        return {"zip": query if "," in query else query + ",US"}, True
    return {"q": query}, False


# ---------- HTTP ----------
def _get(endpoint, params, not_found="City not found. Check the spelling and try again."):
    params = dict(params, appid=get_api_key(), units="metric")
    try:
        resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        raise WeatherError("The request timed out. Check your connection and try again.") from None
    except requests.exceptions.ConnectionError:
        raise WeatherError("Network problem: could not reach OpenWeatherMap.") from None
    except requests.exceptions.RequestException:
        raise WeatherError("Something went wrong while contacting the weather service.") from None

    if resp.status_code == 401:
        raise WeatherError("Invalid API key. Check it, and note that new keys can take a while to activate.")
    if resp.status_code == 404:
        raise WeatherError(not_found)
    if resp.status_code == 429:
        raise WeatherError("Too many requests. Wait a minute and try again.")
    if resp.status_code != 200:
        raise WeatherError(f"The weather service returned an error ({resp.status_code}).")
    try:
        return resp.json()
    except ValueError:
        raise WeatherError("The weather service sent an unreadable response.") from None


# ---------- parsing ----------
def parse_current(data):
    try:
        weather = data["weather"][0]
        return Current(
            city=data["name"],
            country=data.get("sys", {}).get("country", ""),
            temp_c=float(data["main"]["temp"]),
            feels_c=float(data["main"]["feels_like"]),
            humidity=int(data["main"]["humidity"]),
            description=weather["description"].title(),
            wind_ms=float(data.get("wind", {}).get("speed", 0.0)),
            icon=weather["icon"],
            lat=float(data["coord"]["lat"]),
            lon=float(data["coord"]["lon"]),
        )
    except (KeyError, IndexError, TypeError, ValueError):
        raise WeatherError("The weather data came back in an unexpected format.") from None


def parse_forecast(data, now_ts=None):
    """Return (hourly, daily). The free API gives 3-hour steps for 5 days."""
    now_ts = time.time() if now_ts is None else now_ts
    try:
        tz = timezone(timedelta(seconds=int(data["city"]["timezone"])))
        items = data["list"]
        hourly, by_day = [], {}
        for item in items:
            ts = item["dt"]
            local = datetime.fromtimestamp(ts, tz=tz)
            w = item["weather"][0]
            temp = float(item["main"]["temp"])
            if now_ts - 1800 <= ts <= now_ts + 6 * 3600:
                hourly.append(HourlyEntry(local, temp, w["description"].title(), w["icon"]))
            by_day.setdefault(local.date(), []).append((local, item, w))

        today = datetime.fromtimestamp(now_ts, tz=tz).date()
        daily = []
        for day in sorted(d for d in by_day if d > today)[:5]:
            rows = by_day[day]
            lows = [float(i["main"].get("temp_min", i["main"]["temp"])) for _, i, _ in rows]
            highs = [float(i["main"].get("temp_max", i["main"]["temp"])) for _, i, _ in rows]
            _, _, w = min(rows, key=lambda r: abs(r[0].hour - 12))  # entry closest to midday
            daily.append(DailyEntry(day, min(lows), max(highs), w["description"].title(), w["icon"][:2] + "d"))
        return hourly, daily
    except (KeyError, IndexError, TypeError, ValueError):
        raise WeatherError("The forecast data came back in an unexpected format.") from None


# ---------- public functions ----------
def get_current(query):
    query = validate_query(query)
    params, is_zip = build_params(query)
    hint = "ZIP code not found. Add a country code, for example 560001,IN." if is_zip else \
        "City not found. Check the spelling and try again."
    return parse_current(_get("weather", params, not_found=hint))


def get_report(query):
    """Current weather plus hourly and daily forecast for a city name or ZIP code."""
    current = get_current(query)
    forecast = _get("forecast", {"lat": current.lat, "lon": current.lon})
    hourly, daily = parse_forecast(forecast)
    return Report(current, hourly, daily)


def locate_by_ip():
    """Approximate city from the user's public IP address (ipinfo.io, free tier)."""
    try:
        data = requests.get(IPINFO_URL, timeout=TIMEOUT).json()
    except (requests.exceptions.RequestException, ValueError):
        raise WeatherError("Could not detect your location. Type a city instead.") from None
    city = data.get("city") if isinstance(data, dict) else None
    if not city:
        raise WeatherError("Could not detect your location. Type a city instead.")
    return city


def fetch_icon(code):
    """PNG bytes for a weather icon, or None if it can't be downloaded."""
    try:
        resp = requests.get(ICON_URL.format(code=code), timeout=TIMEOUT)
        return resp.content if resp.status_code == 200 else None
    except requests.exceptions.RequestException:
        return None
