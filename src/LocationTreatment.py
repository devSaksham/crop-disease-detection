"""Location-aware treatment plans generated via Groq's LLM API.

Given a crop, its predicted condition, the facts-based severity, and the
farmer's location (manually entered or from browser geolocation), asks an
LLM for a localized treatment plan in Hindi (climate/region-appropriate
advice, locally available products, timing).
"""

import os
from datetime import date

import requests
import streamlit as st
from groq import Groq

_NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
_NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
_GROQ_MODEL = "llama-3.3-70b-versatile"


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

_SYSTEM_PROMPT = {
    "hi": """आप एक अनुभवी कृषि विस्तार अधिकारी (Krishi Vigyan Kendra विशेषज्ञ) हैं, जो भारत के छोटे और मध्यम \
किसानों को फसल रोग प्रबंधन में व्यावहारिक सलाह देते हैं।

- हमेशा हिंदी में, स्पष्ट और संक्षिप्त बिंदुओं में उत्तर दें।
- किसान को छोटे/सीमित बजट वाला मान लें -- सस्ते, स्थानीय रूप से उपलब्ध और जैविक विकल्पों को पहले सुझाएं, \
उसके बाद ही रासायनिक विकल्प दें।
- दी गई जानकारी (गंभीरता, इलाज संभव है या नहीं, तारीख, मौसम, स्थान) के अनुसार सलाह को खास तौर पर उसी स्थिति \
के लिए ढालें -- सामान्य/जेनेरिक सलाह न दें।
- अगर रोग लाइलाज है, तो "इलाज" का वादा न करें; इसके बजाय रोकथाम, संक्रमित हिस्सों को हटाने और आगे फैलने से \
रोकने पर ध्यान केंद्रित करें।
- जवाब में मार्कडाउन हेडिंग (####) और बुलेट पॉइंट्स का उपयोग करें ताकि यह पढ़ने में आसान हो।""",
    "en": """You are an experienced agricultural extension officer (Krishi Vigyan Kendra expert) advising \
small and medium-scale Indian farmers on crop disease management.

- Always respond in English, in clear and concise bullet points.
- Assume the farmer has a small/limited budget -- suggest cheap, locally available, and organic options \
first, then chemical options.
- Tailor the advice specifically to the given context (severity, whether it's curable, date, weather, \
location) -- avoid generic, one-size-fits-all advice.
- If the disease has no cure, don't promise a "cure"; focus instead on containment, removing infected \
parts, and preventing further spread.
- Use markdown headings (####) and bullet points in the response so it's easy to scan.""",
}

_USER_PROMPT_TEMPLATE = {
    "hi": """निम्नलिखित जानकारी के आधार पर एक व्यावहारिक, स्थान-विशिष्ट उपचार योजना दें:

फसल: {crop}
रोग/अवस्था: {condition}
गंभीरता: {severity_level} (रोगजनक प्रकार: {pathogen_type}, इलाज संभव: {curable}, फैलाव दर: {spread_rate}, उपज पर प्रभाव: {yield_impact})
आज की तारीख: {today}
किसान का स्थान: {location}
{weather_block}
कृपया निम्नलिखित शामिल करें:
1. तत्काल कदम (Immediate steps)
2. अनुशंसित दवा/उत्पाद (स्थानीय रूप से उपलब्ध और किफायती विकल्पों सहित)
3. छिड़काव/उपचार का समय और तरीका -- वर्तमान मौसम और आज की तारीख (मौसम/सीजन) को ध्यान में रखकर सही दिन चुनें
4. इस क्षेत्र की जलवायु और मौसम को ध्यान में रखते हुए सावधानियां
5. भविष्य में बचाव के उपाय""",
    "en": """Based on the following information, give a practical, location-specific treatment plan:

Crop: {crop}
Disease/condition: {condition}
Severity: {severity_level} (pathogen type: {pathogen_type}, curable: {curable}, spread rate: {spread_rate}, yield impact: {yield_impact})
Today's date: {today}
Farmer's location: {location}
{weather_block}
Please include:
1. Immediate steps
2. Recommended medicine/product (including locally available, affordable options)
3. Spraying/treatment timing and method -- pick the right day accounting for the current weather and \
today's date/season
4. Precautions specific to this region's climate and current weather
5. Future prevention measures""",
}

_WEATHER_BLOCK_LABEL = {
    "hi": "मौसम की जानकारी (बीता कल, आज, आने वाला कल)",
    "en": "Weather information (yesterday, today, tomorrow)",
}

_NOT_APPLICABLE = {"hi": "लागू नहीं", "en": "N/A"}

_CURABLE_LABELS = {
    "hi": {True: "हां", False: "नहीं -- कोई ज्ञात इलाज नहीं, केवल प्रबंधन/रोकथाम संभव", None: "लागू नहीं"},
    "en": {True: "Yes", False: "No known cure -- only management/containment is possible", None: "N/A"},
}


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
    curable_labels = _CURABLE_LABELS.get(lang, _CURABLE_LABELS["hi"])
    curable = curable_labels.get(severity.get("curable"), na)

    weather_block = ""
    if weather_text:
        weather_block = f"\n{_WEATHER_BLOCK_LABEL.get(lang, _WEATHER_BLOCK_LABEL['hi'])}:\n{weather_text}\n"

    system_prompt = _SYSTEM_PROMPT.get(lang, _SYSTEM_PROMPT["hi"])
    template = _USER_PROMPT_TEMPLATE.get(lang, _USER_PROMPT_TEMPLATE["hi"])
    user_prompt = template.format(
        crop=crop,
        condition=condition,
        severity_level=severity_level,
        pathogen_type=severity.get("pathogen_type") or na,
        curable=curable,
        spread_rate=severity.get("spread_rate") or na,
        yield_impact=severity.get("yield_impact") or na,
        today=date.today().isoformat(),
        location=location,
        weather_block=weather_block,
    )

    try:
        response = client.chat.completions.create(
            model=_GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content, None
    except Exception as e:
        error_prefix = "उपचार योजना प्राप्त करने में त्रुटि हुई" if lang == "hi" else "Error getting treatment plan"
        return None, f"{error_prefix}: {e}"
