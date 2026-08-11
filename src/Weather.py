"""Weather context (yesterday / today / tomorrow) via Open-Meteo.

Open-Meteo's forecast endpoint returns daily aggregates for a requested
date range in a single request -- past_days=1 pulls in yesterday, and the
default forecast horizon covers today and tomorrow, so one call covers all
three days needed here. The API is free and keyless for non-commercial use
(https://open-meteo.com/en/docs), unlike OpenWeatherMap's day-summary
endpoint this replaced, which needed a paid "One Call by Call" subscription.
"""

import requests

_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
_DAILY_VARS = ",".join([
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "cloud_cover_mean",
    "relative_humidity_2m_mean",
])

_DAY_LABELS = {
    "hi": {-1: "कल (बीता हुआ)", 0: "आज", 1: "कल (आने वाला)"},
    "en": {-1: "Yesterday", 0: "Today", 1: "Tomorrow"},
}
_NO_DATA_LABEL = {"hi": "जानकारी उपलब्ध नहीं", "en": "information not available"}
_FIELD_LABELS = {
    "hi": {"temp": "तापमान", "humidity": "आर्द्रता", "precip": "वर्षा", "cloud": "बादल"},
    "en": {"temp": "Temp", "humidity": "Humidity", "precip": "Rain", "cloud": "Cloud"},
}


def get_weather_context(lat, lon):
    """Fetch yesterday/today/tomorrow daily summaries for (lat, lon).

    Returns a dict {-1: {...} or None, 0: ..., 1: ...} keyed by day offset
    from today -- a day is None if its data is missing, so a failure is
    visible rather than silently missing. Returns None outright if the
    request itself fails (network error, bad coordinates, etc).
    """
    try:
        response = requests.get(
            _FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": _DAILY_VARS,
                "timezone": "auto",
                "past_days": 1,
                "forecast_days": 2,
            },
            timeout=6,
        )
        response.raise_for_status()
        daily = response.json()["daily"]
    except Exception:
        return None

    context = {}
    for offset in (-1, 0, 1):
        index = offset + 1  # past_days=1 shifts yesterday to index 0
        try:
            context[offset] = {
                "temp_min": daily["temperature_2m_min"][index],
                "temp_max": daily["temperature_2m_max"][index],
                "humidity": daily["relative_humidity_2m_mean"][index],
                "precip": daily["precipitation_sum"][index],
                "cloud": daily["cloud_cover_mean"][index],
            }
        except (KeyError, IndexError, TypeError):
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
        lines.append(
            f"{day_labels[offset]}: {fields['temp']} {_num(day['temp_min'])}–{_num(day['temp_max'])}°C, "
            f"{fields['humidity']} {_num(day['humidity'], 0)}%, "
            f"{fields['precip']} {_num(day['precip'])}mm, "
            f"{fields['cloud']} {_num(day['cloud'], 0)}%"
        )
    return "\n".join(lines) if any_data else None
