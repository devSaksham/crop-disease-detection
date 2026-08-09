import streamlit as st
st.set_page_config(page_title="फसल एवं रोग सूची", layout="wide")

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
from src.Weather import get_weather_context, format_weather_hi
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
st.sidebar.title("Dashboard")
app_mode = st.sidebar.selectbox("Select Page",["Home","About","Disease Recognition"])

if(app_mode == "Home"):
    st.markdown('<span class="ch-eyebrow">🌿 AI-संचालित रोग पहचान</span>', unsafe_allow_html=True)
    st.title("Crops Disease Prediction System")
    image_path = 'uploads/UI image/home_page.jpeg'
    st.image(image_path, width=850)

    st.markdown("""
    Welcome to the Plant Disease Recognition System! 🌿🔍
    
    Our mission is to help in identifying plant diseases efficiently. Upload an image of a plant, and our system will analyze it to detect any signs of diseases. Together, let's protect our crops and ensure a healthier harvest!

    ### How It Works
    1. **Upload Image:** Go to the **Disease Recognition** page and upload an image of a plant with suspected diseases.
    2. **Analysis:** Our system will process the image using advanced algorithms to identify potential diseases.
    3. **Results:** View the results and recommendations for further action.

    ### Why Choose Us?
    - **Accuracy:** Our system utilizes state-of-the-art machine learning techniques for accurate disease detection.
    - **User-Friendly:** Simple and intuitive interface for seamless user experience.
    - **Fast and Efficient:** Receive results in seconds, allowing for quick decision-making.

    ### Get Started
    Click on the **Disease Recognition** page in the sidebar to upload an image and experience the power of our Plant Disease Recognition System!

    ### About Us
    Learn more about the project, our team, and our goals on the **About** page.
    """)

elif(app_mode == 'About'):
    st.header("About Our Project")
    st.markdown("""
                #### About Dataset
                This dataset is recreated using offline augmentation from the original dataset.The original dataset can be found on this github repo.
                This dataset consists of about 87K rgb images of healthy and diseased crop leaves which is categorized into 38 different classes.The total dataset is divided into 80/20 ratio of training and validation set preserving the directory structure.
                A new directory containing 33 test images is created later for prediction purpose.
                #### Content
                1. train (70295 images)
                2. test (33 images)
                3. validation (17572 images)

                """)
    # Create structured data for table
    data = []
    for cls in class_name:
        parts = cls.split("___")
        crop = parts[0].replace("_", " ")
        condition = parts[1].replace("_", " ") if len(parts) > 1 else "Healthy"
        data.append({"फसल का नाम (Crop)": crop, "रोग/अवस्था (Condition)": condition})

    # Convert to DataFrame
    df = pd.DataFrame(data)

    st.markdown('<span class="ch-eyebrow">🌿 38 Classes</span>', unsafe_allow_html=True)
    st.subheader("List of Every Crop with Disease")

    st.dataframe(df, use_container_width=True)


elif(app_mode=="Disease Recognition"):
    st.header("Disease Recognition")
    test_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    image = None
    if test_image is not None:
        pil_image = Image.open(test_image).convert('RGB')
        st.image(pil_image, caption="Uploaded Image", width=400)

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
        st.warning("Please upload an image file to continue.")

    #Predict button
    if st.button("Predict", type="primary", disabled=image is None):
        st.snow()
        start = time.time()

        result, confidence = prediction_img(image)  # custom_resnet.py
        output = class_name[result]
        crop_hi, condition_hi, _ = _display_names(output)

        st.session_state["prediction"] = {
            "output": output,
            "confidence": confidence,
            "crop_hi": crop_hi,
            "condition_hi": condition_hi,
        }
        # a fresh prediction invalidates any previously generated treatment plan / location / weather
        for key in (
            "treatment_plan", "treatment_plan_error",
            "geo_key", "geo_location",
            "manual_geo_text", "manual_geo_latlon",
            "weather_key", "weather_hi",
        ):
            st.session_state.pop(key, None)

        end = time.time()
        logging.info(f"Prediction Response Time: {end - start:.4f} sec")

    if "prediction" in st.session_state:
        pred = st.session_state["prediction"]
        output = pred["output"]
        severity = compute_severity(output)

        with st.container(border=True):
            st.markdown('<div class="ch-result-anchor"></div><span class="ch-eyebrow">Our Prediction</span>', unsafe_allow_html=True)
            st.success(f"Predicted Class is --->  {output}  (विश्वास: {pred['confidence'] * 100:.1f}%)")
            if severity["level"] == "Healthy":
                st.markdown(
                    f'<span class="ch-eyebrow" style="background:{severity["color"]}22;color:{severity["color"]}">'
                    f'पौधा स्वस्थ है</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<span class="ch-eyebrow" style="background:{severity["color"]}22;color:{severity["color"]}">'
                    f'गंभीरता (Severity): {severity["level_hi"]}</span>',
                    unsafe_allow_html=True,
                )
            treatment(output)

        if severity["level"] != "Healthy":
            st.subheader("स्थान-आधारित उपचार योजना")
            location_mode = st.radio(
                "अपना स्थान कैसे देना चाहते हैं?",
                ["मैन्युअल रूप से दर्ज करें", "मेरा स्थान उपयोग करें (ब्राउज़र)"],
                key="location_mode",
            )

            location_str = None
            lat_lon = None
            if location_mode == "मैन्युअल रूप से दर्ज करें":
                manual_location = st.text_input(
                    "अपना गाँव/शहर, राज्य दर्ज करें",
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
                    st.success(f"पहचाना गया स्थान: {location_str}")
                elif loc_data is None:
                    st.info("स्थान की अनुमति माँगी जा रही है... कृपया अपने ब्राउज़र में अनुमति दें।")
                elif "error" in loc_data:
                    error_messages = {
                        0: "आपका ब्राउज़र स्थान सेवा का समर्थन नहीं करता।",
                        1: "स्थान की अनुमति अस्वीकार कर दी गई। कृपया मैन्युअल रूप से स्थान दर्ज करें।",
                        2: "स्थान की जानकारी उपलब्ध नहीं है।",
                        3: "स्थान प्राप्त करने का समय समाप्त हो गया।",
                    }
                    code = loc_data["error"].get("code", -1)
                    st.warning(error_messages.get(code, "स्थान प्राप्त नहीं हो सका। कृपया मैन्युअल रूप से दर्ज करें।"))

            weather_hi = None
            if lat_lon:
                if st.session_state.get("weather_key") != lat_lon:
                    st.session_state["weather_key"] = lat_lon
                    with st.spinner("मौसम की जानकारी प्राप्त की जा रही है..."):
                        st.session_state["weather_hi"] = format_weather_hi(get_weather_context(*lat_lon))
                weather_hi = st.session_state.get("weather_hi")
                if weather_hi:
                    with st.expander("🌦️ मौसम की जानकारी (बीता कल, आज, आने वाला कल)"):
                        st.text(weather_hi)

            if st.button("उपचार योजना प्राप्त करें", disabled=not location_str):
                with st.spinner("उपचार योजना तैयार की जा रही है..."):
                    plan, error = get_location_treatment_plan(
                        pred["crop_hi"], pred["condition_hi"], severity, location_str, weather_hi
                    )
                if error:
                    st.session_state["treatment_plan_error"] = error
                    st.session_state.pop("treatment_plan", None)
                else:
                    st.session_state["treatment_plan"] = plan
                    st.session_state.pop("treatment_plan_error", None)

            if "treatment_plan" in st.session_state:
                st.markdown("#### स्थान-आधारित उपचार योजना")
                st.markdown(st.session_state["treatment_plan"])
            elif "treatment_plan_error" in st.session_state:
                st.error(st.session_state["treatment_plan_error"])
        #  streamlit run App.py







