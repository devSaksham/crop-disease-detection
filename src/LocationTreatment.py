"""Location-aware treatment plans generated via Groq's LLM API.

Given a crop, its predicted condition, the facts-based severity, and the
farmer's location (manually entered or from browser geolocation), asks an
LLM for a localized treatment plan in Hindi (climate/region-appropriate
advice, locally available products, timing).
"""

import os
import requests
import streamlit as st
from groq import Groq

_NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
_NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
_GROQ_MODEL = "openai/gpt-oss-120b"


def reverse_geocode(lat, lon):
    """Convert lat/lon into a human-readable location string.

    Falls back to raw coordinates if the lookup fails for any reason.
    """
    try:
        response = requests.get(
            _NOMINATIM_REVERSE_URL,
            params={"lat": lat, "lon": lon, "format": "json", "zoom": 10},
            headers={"User-Agent": "cropDisease-app/1.0"},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})
        parts = [
            address.get("village") or address.get("town") or address.get("city") or address.get("county"),
            address.get("state"),
            address.get("country"),
        ]
        parts = [p for p in parts if p]
        if parts:
            return ", ".join(parts)
        display_name = data.get("display_name")
        if display_name:
            return display_name
    except Exception:
        pass
    return f"{lat:.4f}, {lon:.4f}"


def forward_geocode(place):
    """Convert a place name (e.g. a manually entered location) into (lat, lon).

    Returns None if the place can't be resolved.
    """
    try:
        response = requests.get(
            _NOMINATIM_SEARCH_URL,
            params={"q": place, "format": "json", "limit": 1},
            headers={"User-Agent": "cropDisease-app/1.0"},
            timeout=5,
        )
        response.raise_for_status()
        results = response.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception:
        pass
    return None


def _get_api_key():
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        return api_key
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return None


def _client():
    api_key = _get_api_key()
    if not api_key:
        return None
    return Groq(api_key=api_key)


_NO_KEY_ERROR = {
    "hi": "GROQ_API_KEY सेट नहीं है। कृपया एनवायरनमेंट वेरिएबल या Streamlit secrets में इसे जोड़ें।",
    "en": "GROQ_API_KEY is not set. Please add it to your environment variables or Streamlit secrets.",
}

_PROMPT_TEMPLATE = {
    "hi": """आप एक कृषि विशेषज्ञ हैं जो भारतीय किसानों को फसल रोग प्रबंधन में सलाह देते हैं।

निम्नलिखित जानकारी के आधार पर एक व्यावहारिक, स्थान-विशिष्ट उपचार योजना हिंदी में दें:

फसल: {crop}
रोग/अवस्था: {condition}
गंभीरता: {severity_level} (रोगजनक प्रकार: {pathogen_type}, फैलाव दर: {spread_rate}, उपज पर प्रभाव: {yield_impact})
किसान का स्थान: {location}
{weather_block}
कृपया निम्नलिखित शामिल करें:
1. तत्काल कदम (Immediate steps)
2. अनुशंसित दवा/उत्पाद (स्थानीय रूप से उपलब्ध विकल्पों सहित)
3. छिड़काव/उपचार का समय और तरीका -- यदि मौसम की जानकारी दी गई है तो बारिश/नमी को ध्यान में रखकर सही दिन चुनें
4. इस क्षेत्र की जलवायु और मौसम को ध्यान में रखते हुए सावधानियां
5. भविष्य में बचाव के उपाय

जवाब संक्षिप्त, स्पष्ट और व्यावहारिक बिंदुओं में दें।""",
    "en": """You are an agricultural expert advising Indian farmers on crop disease management.

Based on the following information, give a practical, location-specific treatment plan in English:

Crop: {crop}
Disease/condition: {condition}
Severity: {severity_level} (pathogen type: {pathogen_type}, spread rate: {spread_rate}, yield impact: {yield_impact})
Farmer's location: {location}
{weather_block}
Please include:
1. Immediate steps
2. Recommended medicine/product (including locally available options)
3. Spraying/treatment timing and method -- if weather information is given, pick the right day accounting for rain/humidity
4. Precautions specific to this region's climate and current weather
5. Future prevention measures

Keep the answer concise, clear, and in practical bullet points.""",
}

_WEATHER_BLOCK_LABEL = {
    "hi": "मौसम की जानकारी (बीता कल, आज, आने वाला कल)",
    "en": "Weather information (yesterday, today, tomorrow)",
}

_NOT_APPLICABLE = {"hi": "लागू नहीं", "en": "N/A"}


def get_location_treatment_plan(crop, condition, severity, location, weather_text=None, lang="hi"):
    """Ask Groq for a location- and weather-aware treatment plan.

    severity: dict as returned by src.Severity.compute_severity
    weather_text: optional weather summary text from src.Weather.format_weather,
        already formatted in the same `lang`
    lang: "hi" or "en" -- selects both the prompt language and the expected
        response language
    Returns (plan_text, None) on success, or (None, error_message) on failure.
    """
    client = _client()
    if client is None:
        return None, _NO_KEY_ERROR.get(lang, _NO_KEY_ERROR["hi"])

    na = _NOT_APPLICABLE.get(lang, _NOT_APPLICABLE["hi"])
    severity_level = severity.get(f"level_{lang}") or severity.get("level_hi", na)

    weather_block = ""
    if weather_text:
        weather_block = f"\n{_WEATHER_BLOCK_LABEL.get(lang, _WEATHER_BLOCK_LABEL['hi'])}:\n{weather_text}\n"

    template = _PROMPT_TEMPLATE.get(lang, _PROMPT_TEMPLATE["hi"])
    prompt = template.format(
        crop=crop,
        condition=condition,
        severity_level=severity_level,
        pathogen_type=severity.get("pathogen_type") or na,
        spread_rate=severity.get("spread_rate") or na,
        yield_impact=severity.get("yield_impact") or na,
        location=location,
        weather_block=weather_block,
    )

    try:
        response = client.chat.completions.create(
            model=_GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content, None
    except Exception as e:
        error_prefix = "उपचार योजना प्राप्त करने में त्रुटि हुई" if lang == "hi" else "Error getting treatment plan"
        return None, f"{error_prefix}: {e}"
