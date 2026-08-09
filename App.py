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
from src.i18n import t, get_lang, LANGUAGES
from streamlit_js_eval import get_geolocation
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# CauseHouse design-system touches that the native Streamlit theme can't express:
# hard offset "sticker" shadows and uppercase pill chips.
st.markdown("""
<style>
div[data-testid="stButton"] button[kind="primary"] {
    box-shadow: 4px 4px 0px 0px #1D2B1F;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    transition: transform 0.05s ease, box-shadow 0.05s ease;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    transform: translate(-2px, -2px);
    box-shadow: 6px 6px 0px 0px #1D2B1F;
}
div[data-testid="stButton"] button[kind="primary"]:active {
    transform: translate(2px, 2px);
    box-shadow: 2px 2px 0px 0px #1D2B1F;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ch-result-anchor) {
    box-shadow: 4px 4px 0px 0px #1D2B1F;
}
.ch-eyebrow {
    display: inline-block;
    background: #BFEA4B;
    color: #1D2B1F;
    font-family: "Inter", sans-serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 8px 14px;
    border-radius: 9999px;
    margin-bottom: 14px;
}
section[data-testid="stSidebar"] label p {
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 12px;
    font-weight: 700;
    color: #6D7B6F;
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
    # the previous treatment plan was generated in the old language -- drop it
    st.session_state.pop("treatment_plan", None)
    st.session_state.pop("treatment_plan_error", None)

PAGE_KEYS = ["home", "about", "predict"]
app_mode = st.sidebar.selectbox(
    t("select_page"),
    PAGE_KEYS,
    format_func=lambda k: {"home": t("nav_home"), "about": t("nav_about"), "predict": t("nav_predict")}[k],
    key="app_mode",
)

if app_mode == "home":
    st.markdown(f'<span class="ch-eyebrow">{t("home_eyebrow")}</span>', unsafe_allow_html=True)
    st.title(t("home_title"))
    image_path = 'uploads/UI image/home_page.jpeg'
    st.image(image_path, width=850)
    st.markdown(t("home_body"))

elif app_mode == "about":
    st.header(t("about_header"))
    st.markdown(t("about_body"))

    data = []
    for cls in class_name:
        crop, condition, condition_key = _display_names(cls, lang)
        if condition_key == 'healthy':
            condition = t("table_healthy")
        data.append({t("table_crop_col"): crop, t("table_condition_col"): condition})
    df = pd.DataFrame(data)

    st.markdown(f'<span class="ch-eyebrow">{t("about_eyebrow")}</span>', unsafe_allow_html=True)
    st.subheader(t("about_subheader"))
    st.dataframe(df, use_container_width=True)


elif app_mode == "predict":
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
        # a fresh prediction invalidates any previously generated treatment plan / location / weather
        for key in (
            "treatment_plan", "treatment_plan_error",
            "geo_key", "geo_location",
            "manual_geo_text", "manual_geo_latlon",
            "weather_key", "weather_context",
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
            treatment(output, lang)

        if severity["level"] != "Healthy":
            st.subheader(t("location_section_header"))
            LOCATION_MODE_KEYS = ["manual", "gps"]
            location_mode = st.radio(
                t("location_mode_label"),
                LOCATION_MODE_KEYS,
                format_func=lambda k: t("location_mode_manual") if k == "manual" else t("location_mode_gps"),
                key="location_mode",
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
                st.markdown(f"#### {t('plan_header')}")
                st.markdown(st.session_state["treatment_plan"])
            elif "treatment_plan_error" in st.session_state:
                st.error(st.session_state["treatment_plan_error"])
        #  streamlit run App.py
