"""Facts-based severity scoring for the 38 PlantVillage disease classes.

Severity is derived from real plant-pathology attributes of each disease
(pathogen type, curability, spread rate, yield impact) rather than from
model confidence or randomness, so the same disease always gets the same
severity regardless of how confident the model was.
"""

# score contribution per spread-rate / yield-impact bucket
_SPREAD_SCORE = {"Low": 1, "Medium": 2, "High": 3}
_IMPACT_SCORE = {"Low": 1, "Medium": 2, "High": 3, "Severe": 4}

# facts keyed by the same 'Crop___Condition' strings used in class_name / Treatment.py
# pathogen_type: fungal | bacterial | viral | oomycete | pest
SEVERITY_FACTS = {
    "Apple___Apple_scab": {"pathogen_type": "fungal", "curable": True, "spread_rate": "Medium", "yield_impact": "Medium"},
    "Apple___Black_rot": {"pathogen_type": "fungal", "curable": True, "spread_rate": "Medium", "yield_impact": "High"},
    "Apple___Cedar_apple_rust": {"pathogen_type": "fungal", "curable": True, "spread_rate": "Low", "yield_impact": "Low"},

    "Cherry_(including_sour)___Powdery_mildew": {"pathogen_type": "fungal", "curable": True, "spread_rate": "Medium", "yield_impact": "Low"},

    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {"pathogen_type": "fungal", "curable": True, "spread_rate": "Medium", "yield_impact": "High"},
    "Corn_(maize)___Common_rust_": {"pathogen_type": "fungal", "curable": True, "spread_rate": "Medium", "yield_impact": "Medium"},
    "Corn_(maize)___Northern_Leaf_Blight": {"pathogen_type": "fungal", "curable": True, "spread_rate": "High", "yield_impact": "High"},

    "Grape___Black_rot": {"pathogen_type": "fungal", "curable": True, "spread_rate": "High", "yield_impact": "High"},
    "Grape___Esca_(Black_Measles)": {"pathogen_type": "fungal", "curable": False, "spread_rate": "Medium", "yield_impact": "High"},
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {"pathogen_type": "fungal", "curable": True, "spread_rate": "Low", "yield_impact": "Low"},

    "Orange___Haunglongbing_(Citrus_greening)": {"pathogen_type": "bacterial", "curable": False, "spread_rate": "High", "yield_impact": "Severe"},

    "Peach___Bacterial_spot": {"pathogen_type": "bacterial", "curable": True, "spread_rate": "High", "yield_impact": "High"},

    "Pepper,_bell___Bacterial_spot": {"pathogen_type": "bacterial", "curable": True, "spread_rate": "High", "yield_impact": "High"},

    "Potato___Early_blight": {"pathogen_type": "fungal", "curable": True, "spread_rate": "Medium", "yield_impact": "Medium"},
    "Potato___Late_blight": {"pathogen_type": "oomycete", "curable": True, "spread_rate": "High", "yield_impact": "Severe"},

    "Squash___Powdery_mildew": {"pathogen_type": "fungal", "curable": True, "spread_rate": "High", "yield_impact": "Medium"},

    "Strawberry___Leaf_scorch": {"pathogen_type": "fungal", "curable": True, "spread_rate": "Medium", "yield_impact": "Medium"},

    "Tomato___Bacterial_spot": {"pathogen_type": "bacterial", "curable": True, "spread_rate": "High", "yield_impact": "High"},
    "Tomato___Early_blight": {"pathogen_type": "fungal", "curable": True, "spread_rate": "Medium", "yield_impact": "Medium"},
    "Tomato___Late_blight": {"pathogen_type": "oomycete", "curable": True, "spread_rate": "High", "yield_impact": "Severe"},
    "Tomato___Leaf_Mold": {"pathogen_type": "fungal", "curable": True, "spread_rate": "Low", "yield_impact": "Low"},
    "Tomato___Septoria_leaf_spot": {"pathogen_type": "fungal", "curable": True, "spread_rate": "Medium", "yield_impact": "Medium"},
    "Tomato___Spider_mites Two-spotted_spider_mite": {"pathogen_type": "pest", "curable": True, "spread_rate": "High", "yield_impact": "Medium"},
    "Tomato___Target_Spot": {"pathogen_type": "fungal", "curable": True, "spread_rate": "Medium", "yield_impact": "Medium"},
    "Tomato___Tomato_mosaic_virus": {"pathogen_type": "viral", "curable": False, "spread_rate": "Medium", "yield_impact": "High"},
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {"pathogen_type": "viral", "curable": False, "spread_rate": "High", "yield_impact": "Severe"},
}

# healthy classes: no disease, no severity
_HEALTHY_CLASSES = {
    "Apple___healthy", "Blueberry___healthy", "Cherry_(including_sour)___healthy",
    "Corn_(maize)___healthy", "Grape___healthy", "Peach___healthy",
    "Pepper,_bell___healthy", "Potato___healthy", "Raspberry___healthy",
    "Soybean___healthy", "Strawberry___healthy", "Tomato___healthy",
}

LEVEL_INFO = {
    "Critical": {"label_hi": "गंभीर", "color": "#B3261E"},
    "High": {"label_hi": "उच्च", "color": "#E8590C"},
    "Medium": {"label_hi": "मध्यम", "color": "#C9971C"},
    "Low": {"label_hi": "निम्न", "color": "#2F7D32"},
    "Healthy": {"label_hi": "स्वस्थ", "color": "#2F7D32"},
}


def _band(score):
    if score >= 8:
        return "Critical"
    if score >= 6:
        return "High"
    if score >= 4:
        return "Medium"
    return "Low"


def compute_severity(class_key):
    """Return facts-based severity info for a 'Crop___Condition' class key.

    Returns a dict with: level, level_hi, color, score, pathogen_type,
    curable, spread_rate, yield_impact. For healthy classes, level is
    'Healthy' and score/pathogen fields are None.
    """
    if class_key in _HEALTHY_CLASSES:
        info = LEVEL_INFO["Healthy"]
        return {
            "level": "Healthy",
            "level_hi": info["label_hi"],
            "color": info["color"],
            "score": None,
            "pathogen_type": None,
            "curable": None,
            "spread_rate": None,
            "yield_impact": None,
        }

    facts = SEVERITY_FACTS.get(class_key)
    if facts is None:
        # unknown class key: no facts available
        return {
            "level": "Unknown",
            "level_hi": "अज्ञात",
            "color": "#6D7B6F",
            "score": None,
            "pathogen_type": None,
            "curable": None,
            "spread_rate": None,
            "yield_impact": None,
        }

    score = (
        _SPREAD_SCORE[facts["spread_rate"]]
        + _IMPACT_SCORE[facts["yield_impact"]]
        + (0 if facts["curable"] else 2)
    )
    level = _band(score)
    info = LEVEL_INFO[level]

    return {
        "level": level,
        "level_hi": info["label_hi"],
        "color": info["color"],
        "score": score,
        "pathogen_type": facts["pathogen_type"],
        "curable": facts["curable"],
        "spread_rate": facts["spread_rate"],
        "yield_impact": facts["yield_impact"],
    }
