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

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
_GROQ_MODEL = "llama-3.3-70b-versatile"


def reverse_geocode(lat, lon):
    """Convert lat/lon into a human-readable location string.

    Falls back to raw coordinates if the lookup fails for any reason.
    """
    try:
        response = requests.get(
            _NOMINATIM_URL,
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


def get_location_treatment_plan(crop, condition, severity, location):
    """Ask Groq for a location-aware Hindi treatment plan.

    severity: dict as returned by src.Severity.compute_severity
    Returns (plan_text, None) on success, or (None, error_message) on failure.
    """
    client = _client()
    if client is None:
        return None, "GROQ_API_KEY सेट नहीं है। कृपया एनवायरनमेंट वेरिएबल या Streamlit secrets में इसे जोड़ें।"

    severity_line = (
        f"गंभीरता: {severity.get('level_hi', 'अज्ञात')} "
        f"(रोगजनक प्रकार: {severity.get('pathogen_type') or 'लागू नहीं'}, "
        f"फैलाव दर: {severity.get('spread_rate') or 'लागू नहीं'}, "
        f"उपज पर प्रभाव: {severity.get('yield_impact') or 'लागू नहीं'})"
    )

    prompt = f"""आप एक कृषि विशेषज्ञ हैं जो भारतीय किसानों को फसल रोग प्रबंधन में सलाह देते हैं।

निम्नलिखित जानकारी के आधार पर एक व्यावहारिक, स्थान-विशिष्ट उपचार योजना हिंदी में दें:

फसल: {crop}
रोग/अवस्था: {condition}
{severity_line}
किसान का स्थान: {location}

कृपया निम्नलिखित शामिल करें:
1. तत्काल कदम (Immediate steps)
2. अनुशंसित दवा/उत्पाद (स्थानीय रूप से उपलब्ध विकल्पों सहित)
3. छिड़काव/उपचार का समय और तरीका
4. इस क्षेत्र की जलवायु को ध्यान में रखते हुए सावधानियां
5. भविष्य में बचाव के उपाय

जवाब संक्षिप्त, स्पष्ट और व्यावहारिक बिंदुओं में दें।"""

    try:
        response = client.chat.completions.create(
            model=_GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, f"उपचार योजना प्राप्त करने में त्रुटि हुई: {e}"
