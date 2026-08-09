"""Weather context (yesterday / today / tomorrow) via OpenWeatherMap.

Uses the One Call API 3.0 "day summary" endpoint, which returns an
aggregated summary for a single date -- past, present, or future -- in a
uniform shape. That lets yesterday/today/tomorrow be fetched with the same
function instead of mixing separate "current" and "historical" endpoints.
"""

import os
from datetime import date, timedelta

import requests
import streamlit as st

_DAY_SUMMARY_URL = "https://api.openweathermap.org/data/3.0/onecall/day_summary"

_DAY_LABELS_HI = {-1: "कल (बीता हुआ)", 0: "आज", 1: "कल (आने वाला)"}


def _get_api_key():
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if api_key:
        return api_key
    try:
        return st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        return None


def _fetch_day_summary(lat, lon, day_str, api_key):
    response = requests.get(
        _DAY_SUMMARY_URL,
        params={"lat": lat, "lon": lon, "date": day_str, "units": "metric", "appid": api_key},
        timeout=6,
    )
    response.raise_for_status()
    return response.json()


def get_weather_context(lat, lon):
    """Fetch yesterday/today/tomorrow day summaries for (lat, lon).

    Returns a dict {-1: {...} or None, 0: ..., 1: ...} keyed by day offset
    from today -- a day is None if its fetch failed, so a failure is visible
    rather than silently missing. Returns None outright if
    OPENWEATHER_API_KEY isn't configured.

    Note: the day_summary endpoint's forward-looking behavior (offset +1,
    "tomorrow") is documented by OpenWeatherMap as supported up to ~1.5
    years ahead, but this has not been exercised against a live API key in
    this codebase -- treat the "tomorrow" figures as unverified until
    checked against a real response.
    """
    api_key = _get_api_key()
    if not api_key:
        return None

    today = date.today()
    context = {}
    for offset in (-1, 0, 1):
        day_str = (today + timedelta(days=offset)).isoformat()
        try:
            context[offset] = _fetch_day_summary(lat, lon, day_str, api_key)
        except Exception:
            context[offset] = None
    return context


def _num(value, decimals=1):
    if value is None:
        return "?"
    try:
        return f"{round(float(value), decimals)}"
    except (TypeError, ValueError):
        return "?"


def format_weather_hi(context):
    """Render a weather context dict (from get_weather_context) as Hindi text.

    Days that failed to fetch are called out explicitly (not omitted) so a
    missing "tomorrow" forecast doesn't silently drop out of the prompt.
    """
    if not context:
        return None

    lines = []
    any_data = False
    for offset in (-1, 0, 1):
        day = context.get(offset)
        if not day:
            lines.append(f"{_DAY_LABELS_HI[offset]}: जानकारी उपलब्ध नहीं")
            continue
        any_data = True
        temp = day.get("temperature", {})
        humidity = day.get("humidity", {})
        precip = day.get("precipitation", {})
        cloud = day.get("cloud_cover", {})
        lines.append(
            f"{_DAY_LABELS_HI[offset]}: तापमान {_num(temp.get('min'))}–{_num(temp.get('max'))}°C, "
            f"आर्द्रता {_num(humidity.get('afternoon'), 0)}%, "
            f"वर्षा {_num(precip.get('total'))}mm, "
            f"बादल {_num(cloud.get('afternoon'), 0)}%"
        )
    return "\n".join(lines) if any_data else None
