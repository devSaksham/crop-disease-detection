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

_DAY_LABELS = {
    "hi": {-1: "कल (बीता हुआ)", 0: "आज", 1: "कल (आने वाला)"},
    "en": {-1: "Yesterday", 0: "Today", 1: "Tomorrow"},
}
_NO_DATA_LABEL = {"hi": "जानकारी उपलब्ध नहीं", "en": "information not available"}
_FIELD_LABELS = {
    "hi": {"temp": "तापमान", "humidity": "आर्द्रता", "precip": "वर्षा", "cloud": "बादल"},
    "en": {"temp": "Temp", "humidity": "Humidity", "precip": "Rain", "cloud": "Cloud"},
}


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

    Note: this endpoint requires OpenWeatherMap's separate "One Call by
    Call" subscription -- a plain/free-tier API key gets HTTP 401 on every
    call here (all three offsets fail identically), verified live. If your
    key isn't subscribed to that plan, every day comes back None and
    format_weather() returns None -- the app degrades gracefully, but no
    weather context reaches the treatment plan until you subscribe at
    https://openweathermap.org/price.
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


def format_weather(context, lang="hi"):
    """Render a weather context dict (from get_weather_context) as text.

    Days that failed to fetch are called out explicitly (not omitted) so a
    missing "tomorrow" forecast doesn't silently drop out of the prompt.
    Callers should cache the raw `context` dict, not this formatted string,
    and re-format at render/prompt time so a language switch doesn't serve
    stale-language text.
    """
    if not context:
        return None

    day_labels = _DAY_LABELS[lang]
    fields = _FIELD_LABELS[lang]
    lines = []
    any_data = False
    for offset in (-1, 0, 1):
        day = context.get(offset)
        if not day:
            lines.append(f"{day_labels[offset]}: {_NO_DATA_LABEL[lang]}")
            continue
        any_data = True
        temp = day.get("temperature", {})
        humidity = day.get("humidity", {})
        precip = day.get("precipitation", {})
        cloud = day.get("cloud_cover", {})
        lines.append(
            f"{day_labels[offset]}: {fields['temp']} {_num(temp.get('min'))}–{_num(temp.get('max'))}°C, "
            f"{fields['humidity']} {_num(humidity.get('afternoon'), 0)}%, "
            f"{fields['precip']} {_num(precip.get('total'))}mm, "
            f"{fields['cloud']} {_num(cloud.get('afternoon'), 0)}%"
        )
    return "\n".join(lines) if any_data else None
