import streamlit as st
st.set_page_config(page_title="फसल एवं रोग सूची / Crop Disease System", layout="wide")

import pandas as pd
import time
import logging
logging.basicConfig(level=logging.INFO)
import warnings
warnings.filterwarnings('ignore')

from dotenv import load_dotenv
load_dotenv()

import torch
from torchvision import transforms
from PIL import Image
from src.custom_resnet import prediction_img

from src.Treatment import treatment, _display_names
from src.Severity import compute_severity
from src.LocationTreatment import reverse_geocode, forward_geocode, get_location_treatment_plan
from src.Weather import get_weather_context, format_weather
from src.Speech import synthesize_speech
from src.i18n import t, get_lang, LANGUAGES
from streamlit_js_eval import get_geolocation
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Apple-style design-system touches the native Streamlit theme can't express:
# translucent materials, restrained system typography, and instant press feedback
# instead of the previous neo-brutalist offset shadows.
st.markdown("""
<style>
:root {
    --apple-surface: rgba(255, 255, 255, 0.72);
    --apple-border: rgba(0, 0, 0, 0.08);
    --apple-text-secondary: #6E6E73;
    --apple-accent: #34C759;
    --apple-accent-tint: rgba(52, 199, 89, 0.12);
    --apple-accent-text: #1D7A34;
    --apple-ease: cubic-bezier(0.16, 1, 0.3, 1);
}

html, body, [class*="css"], .stApp {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display",
        system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Typography: tracking and leading are size-specific, never one fixed value */
h1 { font-weight: 700; letter-spacing: -0.02em; line-height: 1.08; }
h2 { font-weight: 600; letter-spacing: -0.015em; line-height: 1.15; }
h3, h4 { font-weight: 600; letter-spacing: -0.01em; line-height: 1.25; }
p, li, span, label { letter-spacing: 0; line-height: 1.5; }

/* Buttons: feedback lives on the press and is instant, settle is critically damped (no bounce) */
div[data-testid="stButton"] button {
    transition: transform 0.15s var(--apple-ease), box-shadow 0.15s var(--apple-ease),
        background-color 0.15s var(--apple-ease), border-color 0.15s var(--apple-ease);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}
div[data-testid="stButton"] button:hover {
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.10);
}
div[data-testid="stButton"] button:active {
    transform: scale(0.97);
    transition: transform 0.08s ease-out;
}

/* Result card: a translucent material layer, not a hard-offset sticker shadow */
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ch-result-anchor) {
    background: var(--apple-surface);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--apple-border);
    border-top: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    transition: box-shadow 0.3s var(--apple-ease);
}

/* Eyebrow pill: soft tinted chip instead of a solid brutalist tag */
.ch-eyebrow {
    display: inline-block;
    background: var(--apple-accent-tint);
    color: var(--apple-accent-text);
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.01em;
    padding: 6px 12px;
    border-radius: 9999px;
    margin-bottom: 14px;
}

/* Sidebar: translucent chrome, content conceptually scrolls under it */
section[data-testid="stSidebar"] {
    background: var(--apple-surface);
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border-right: 1px solid var(--apple-border);
}
section[data-testid="stSidebar"] label p {
    text-transform: none;
    letter-spacing: 0.01em;
    font-size: 12px;
    font-weight: 600;
    color: var(--apple-text-secondary);
}

/* Primary navigation: a translucent segmented bar, not an underlined tab strip.
   Streamlit 1.61 renders tabs via React Aria: [role="tablist"] > [data-testid="stTab"],
   with a .react-aria-SelectionIndicator underline riding under the active tab. */
div[data-testid="stTabs"] [role="tablist"] {
    display: inline-flex;
    gap: 2px;
    background: var(--apple-surface);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--apple-border);
    border-radius: 9999px;
    padding: 4px;
    width: fit-content;
}
div[data-testid="stTabs"] [data-testid="stTab"] {
    height: auto;
    padding: 8px 20px;
    border-radius: 9999px;
    font-weight: 600;
    color: var(--apple-text-secondary);
    transition: background-color 0.2s var(--apple-ease), color 0.2s var(--apple-ease),
        box-shadow 0.2s var(--apple-ease);
}
div[data-testid="stTabs"] [data-testid="stTab"] p {
    font-weight: 600;
    letter-spacing: -0.005em;
}
div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
    background: #FFFFFF;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
}
div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] p {
    color: #1D1D1F;
}
div[data-testid="stTabs"] .react-aria-SelectionIndicator {
    display: none;
}
div[data-testid="stTabs"] { margin-bottom: 8px; }

/* Language / location toggles: a segmented pill control, not stacked radio bullets.
   Still a plain st.radio underneath -- st.segmented_control allows deselecting to
   None, which would crash the f"level_{lang}" lookups downstream. */
div[data-testid="stRadio"] div[data-testid="stRadioGroup"] {
    display: inline-flex;
    background: var(--apple-surface);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--apple-border);
    border-radius: 9999px;
    padding: 4px;
    gap: 2px;
}
div[data-testid="stRadioGroup"] label[data-testid="stRadioOption"] {
    margin: 0;
    padding: 6px 16px;
    border-radius: 9999px;
    transition: background-color 0.2s var(--apple-ease), box-shadow 0.2s var(--apple-ease);
}
div[data-testid="stRadioGroup"] label[data-testid="stRadioOption"]:has(input:checked) {
    background: #FFFFFF;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
}
/* the visual circle indicator is a leaf <div> immediately before the text's
   stMarkdownContainer, several levels deep -- target it by sibling position
   so nesting depth doesn't matter. The input stays in the DOM (display:none
   would risk losing native label-click-to-toggle behavior). */
div[data-testid="stRadioGroup"] label[data-testid="stRadioOption"] div:has(+ [data-testid="stMarkdownContainer"]) {
    display: none;
}

/* Upload dropzone: a calm material card instead of the bare native control */
[data-testid="stFileUploaderDropzone"] {
    background: var(--apple-surface);
    border: 1px solid var(--apple-border);
    border-radius: 16px;
    transition: box-shadow 0.2s var(--apple-ease), border-color 0.2s var(--apple-ease);
}
[data-testid="stFileUploaderDropzone"]:hover {
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
    border-color: var(--apple-accent);
}

/* Reduced motion: keep feedback, drop the motion */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
    }
    div[data-testid="stButton"] button:active,
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ch-result-anchor) {
        transform: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

class_name = ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
                       'Blueberry___healthy', 'Cherry_(including_sour)___healthy', 'Cherry_(including_sour)___Powdery_mildew',
                       'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_', 'Corn_(maize)___healthy',
                       'Corn_(maize)___Northern_Leaf_Blight', 'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___healthy',
                       'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Orange___Haunglongbing_(Citrus_greening)',
                         'Peach___Bacterial_spot', 'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
                         'Potato___Early_blight', 'Potato___healthy', 'Potato___Late_blight', 'Raspberry___healthy',
                           'Soybean___healthy', 'Squash___Powdery_mildew', 'Strawberry___healthy', 'Strawberry___Leaf_scorch',
                           'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___healthy', 'Tomato___Late_blight',
                           'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
                      'Tomato___Target_Spot', 'Tomato___Tomato_mosaic_virus', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus']

# The 15 crop/disease classes from the current training notebook
# (plantvillage_disease_detection_ran.ipynb, Kaggle emmarex/plantdisease
# dataset -- Pepper/Potato/Tomato only). Shown on the About tab; kept
# separate from `class_name` above, which indexes the deployed model's
# 38-class output and must not change.
about_class_name = ['Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
                     'Potato___Early_blight', 'Potato___healthy', 'Potato___Late_blight',
                     'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___healthy',
                     'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot',
                     'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot',
                     'Tomato___Tomato_mosaic_virus', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus']


#Sidebar.............................................................
st.sidebar.title(t("dashboard_title"))

lang = st.sidebar.radio(
    t("language_label"),
    list(LANGUAGES.keys()),
    format_func=lambda k: LANGUAGES[k],
    key="lang",
    horizontal=True,
)
if st.session_state.get("_prev_lang") != lang:
    st.session_state["_prev_lang"] = lang
    # the previous treatment plan (and any audio read from it) was generated
    # in the old language -- drop it
    st.session_state.pop("treatment_plan", None)
    st.session_state.pop("treatment_plan_error", None)
    st.session_state.pop("prediction_audio_key", None)
    st.session_state.pop("prediction_audio_bytes", None)
    st.session_state.pop("plan_audio_key", None)
    st.session_state.pop("plan_audio_bytes", None)

# Primary navigation: a modern top tab bar (styled as an Apple segmented bar
# above) instead of a sidebar page picker.
tab_home, tab_about, tab_predict = st.tabs([t("nav_home"), t("nav_about"), t("nav_predict")])

with tab_home:
    st.markdown(f'<span class="ch-eyebrow">{t("home_eyebrow")}</span>', unsafe_allow_html=True)
    st.title(t("home_title"))
    image_path = 'uploads/UI image/home_page.jpeg'
    st.image(image_path, width=850)
    st.markdown(t("home_body"))

with tab_about:
    st.header(t("about_header"))
    st.markdown(t("about_body"))

    data = []
    for cls in about_class_name:
        crop, condition, condition_key = _display_names(cls, lang)
        if condition_key == 'healthy':
            condition = t("table_healthy")
        data.append({t("table_crop_col"): crop, t("table_condition_col"): condition})
    df = pd.DataFrame(data)

    st.markdown(f'<span class="ch-eyebrow">{t("about_eyebrow")}</span>', unsafe_allow_html=True)
    st.subheader(t("about_subheader"))
    st.dataframe(df, use_container_width=True)

with tab_predict:
    st.header(t("predict_header"))
    test_image = st.file_uploader(t("upload_label"), type=["jpg", "jpeg", "png"], key="image_uploader")

    image = None
    if test_image is not None:
        pil_image = Image.open(test_image).convert('RGB')
        st.image(pil_image, caption=t("upload_caption"), width=400)

        transform = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])
        # for moving data to device (CPU or GPU)
        def to_device(data, device):
            """Move tensor(s) to chosen device"""
            if isinstance(data, (list,tuple)):
                return [to_device(x, device) for x in data]
            return data.to(device, non_blocking=True)


        image = transform(pil_image)
        image = image.unsqueeze(0)  # Add batch dimension [1, 3, 224, 224]
        image = to_device(image, device)
    else:
        st.warning(t("upload_warning"))

    #Predict button
    if st.button(t("predict_button"), type="primary", disabled=image is None, key="predict_btn"):
        st.snow()
        start = time.time()

        result, confidence = prediction_img(image)  # custom_resnet.py
        output = class_name[result]

        st.session_state["prediction"] = {"output": output, "confidence": confidence}
        # a fresh prediction invalidates any previously generated treatment plan / location / weather / audio
        for key in (
            "treatment_plan", "treatment_plan_error",
            "geo_key", "geo_location",
            "manual_geo_text", "manual_geo_latlon",
            "weather_key", "weather_context",
            "prediction_audio_key", "prediction_audio_bytes",
            "plan_audio_key", "plan_audio_bytes",
        ):
            st.session_state.pop(key, None)

        end = time.time()
        logging.info(f"Prediction Response Time: {end - start:.4f} sec")

    if "prediction" in st.session_state:
        pred = st.session_state["prediction"]
        output = pred["output"]
        severity = compute_severity(output)
        crop_name, condition_name, _ = _display_names(output, lang)

        with st.container(border=True):
            st.markdown(f'<div class="ch-result-anchor"></div><span class="ch-eyebrow">{t("prediction_eyebrow")}</span>', unsafe_allow_html=True)
            st.success(f"{t('predicted_class')}: {output}  ({t('confidence')}: {pred['confidence'] * 100:.1f}%)")
            if severity["level"] == "Healthy":
                st.markdown(
                    f'<span class="ch-eyebrow" style="background:{severity["color"]}22;color:{severity["color"]}">'
                    f'{t("plant_healthy")}</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<span class="ch-eyebrow" style="background:{severity["color"]}22;color:{severity["color"]}">'
                    f'{t("severity_label")}: {severity[f"level_{lang}"]}</span>',
                    unsafe_allow_html=True,
                )
            treatment_text = treatment(output, lang)

            prediction_audio_key = (output, lang)
            if st.button(t("listen_prediction_button"), key="listen_prediction_btn"):
                spoken_summary = t(
                    "prediction_summary_spoken",
                    crop=crop_name, condition=condition_name, severity=severity[f"level_{lang}"],
                )
                with st.spinner(t("audio_generating")):
                    st.session_state["prediction_audio_bytes"] = synthesize_speech(
                        f"{spoken_summary} {treatment_text}", lang
                    )
                st.session_state["prediction_audio_key"] = prediction_audio_key

            if st.session_state.get("prediction_audio_key") == prediction_audio_key:
                audio_bytes = st.session_state.get("prediction_audio_bytes")
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                else:
                    st.warning(t("audio_unavailable"))

        if severity["level"] != "Healthy":
            st.subheader(t("location_section_header"))
            LOCATION_MODE_KEYS = ["manual", "gps"]
            location_mode = st.radio(
                t("location_mode_label"),
                LOCATION_MODE_KEYS,
                format_func=lambda k: t("location_mode_manual") if k == "manual" else t("location_mode_gps"),
                key="location_mode",
                horizontal=True,
            )

            location_str = None
            lat_lon = None
            if location_mode == "manual":
                manual_location = st.text_input(
                    t("location_input_label"),
                    key="manual_location",
                )
                location_str = manual_location.strip() or None
                if location_str:
                    if st.session_state.get("manual_geo_text") != location_str:
                        st.session_state["manual_geo_text"] = location_str
                        st.session_state["manual_geo_latlon"] = forward_geocode(location_str)
                    lat_lon = st.session_state.get("manual_geo_latlon")
            else:
                loc_data = get_geolocation(component_key="crop_disease_geolocation")
                if loc_data and "coords" in loc_data:
                    coords = loc_data["coords"]
                    geo_key = (round(coords["latitude"], 4), round(coords["longitude"], 4))
                    if st.session_state.get("geo_key") != geo_key:
                        st.session_state["geo_key"] = geo_key
                        st.session_state["geo_location"] = reverse_geocode(*geo_key)

                if st.session_state.get("geo_location"):
                    location_str = st.session_state["geo_location"]
                    lat_lon = st.session_state.get("geo_key")
                    st.success(t("location_detected", location=location_str))
                elif loc_data is None:
                    st.info(t("geo_waiting"))
                elif "error" in loc_data:
                    code = loc_data["error"].get("code", -1)
                    st.warning(t(f"geo_error_{code}") if code in (0, 1, 2, 3) else t("geo_error_default"))

            weather_text = None
            if lat_lon:
                if st.session_state.get("weather_key") != lat_lon:
                    st.session_state["weather_key"] = lat_lon
                    with st.spinner(t("weather_fetching")):
                        st.session_state["weather_context"] = get_weather_context(*lat_lon)
                weather_context = st.session_state.get("weather_context")
                weather_text = format_weather(weather_context, lang)
                if weather_text:
                    with st.expander(t("weather_expander")):
                        st.text(weather_text)

            if st.button(t("get_plan_button"), disabled=not location_str, key="get_plan_btn"):
                with st.spinner(t("plan_generating")):
                    plan, error = get_location_treatment_plan(
                        crop_name, condition_name, severity, location_str, weather_text, lang
                    )
                if error:
                    st.session_state["treatment_plan_error"] = error
                    st.session_state.pop("treatment_plan", None)
                else:
                    st.session_state["treatment_plan"] = plan
                    st.session_state.pop("treatment_plan_error", None)

            if "treatment_plan" in st.session_state:
                plan_text = st.session_state["treatment_plan"]
                st.markdown(f"#### {t('plan_header')}")
                st.markdown(plan_text)

                plan_audio_key = (plan_text, lang)
                if st.button(t("listen_plan_button"), key="listen_plan_btn"):
                    with st.spinner(t("audio_generating")):
                        st.session_state["plan_audio_bytes"] = synthesize_speech(plan_text, lang)
                    st.session_state["plan_audio_key"] = plan_audio_key

                if st.session_state.get("plan_audio_key") == plan_audio_key:
                    audio_bytes = st.session_state.get("plan_audio_bytes")
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                    else:
                        st.warning(t("audio_unavailable"))
            elif "treatment_plan_error" in st.session_state:
                st.error(st.session_state["treatment_plan_error"])
        #  streamlit run App.py
