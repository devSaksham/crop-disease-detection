"""UI string translations for the Hindi/English language toggle.

Usage: `from src.i18n import t` then `t("key")` or `t("key", name=value)`
for strings with placeholders. Reads the active language from
st.session_state["lang"] (defaults to "hi").
"""

import streamlit as st

LANGUAGES = {"hi": "हिंदी", "en": "English"}

_STRINGS = {
    "language_label": {"hi": "भाषा / Language", "en": "भाषा / Language"},

    "dashboard_title": {"hi": "डैशबोर्ड", "en": "Dashboard"},
    "nav_home": {"hi": "होम", "en": "Home"},
    "nav_about": {"hi": "जानकारी", "en": "About"},
    "nav_predict": {"hi": "रोग पहचान", "en": "Disease Recognition"},

    "home_eyebrow": {"hi": "🌿 AI-संचालित रोग पहचान", "en": "🌿 AI-Powered Disease Recognition"},
    "home_title": {"hi": "फसल रोग पूर्वानुमान प्रणाली", "en": "Crops Disease Prediction System"},
    "home_body": {
        "hi": """
पौध रोग पहचान प्रणाली में आपका स्वागत है! 🌿🔍

हमारा उद्देश्य फसल रोगों की पहचान को तेज़ और आसान बनाना है। पौधे की एक तस्वीर अपलोड करें, और हमारी प्रणाली रोग के किसी भी लक्षण का विश्लेषण करेगी। आइए मिलकर अपनी फसलों की रक्षा करें और बेहतर उपज सुनिश्चित करें!

### यह कैसे काम करता है
1. **तस्वीर अपलोड करें:** ऊपर **रोग पहचान** टैब पर जाएं और संदिग्ध रोग वाले पौधे की तस्वीर अपलोड करें।
2. **विश्लेषण:** हमारी प्रणाली उन्नत एल्गोरिदम का उपयोग करके संभावित रोगों की पहचान करेगी।
3. **परिणाम:** परिणाम और आगे की कार्रवाई के लिए सुझाव देखें।

### हमें क्यों चुनें?
- **सटीकता:** मिर्च, आलू और टमाटर की 15 फसल/रोग श्रेणियों पर प्रशिक्षित मॉडल, जिसने परीक्षण डेटा पर 95%+ सटीकता हासिल की है।
- **उपयोग में आसान:** सहज और सरल इंटरफ़ेस।
- **तेज़ और कुशल:** कुछ ही सेकंड में परिणाम, तुरंत निर्णय लेने में मदद।

### शुरू करें
ऊपर **रोग पहचान** टैब पर क्लिक करें और अपने पौधों के लिए हमारी प्रणाली का लाभ उठाएं!

### हमारे बारे में
प्रोजेक्ट, डेटासेट और मॉडल के प्रदर्शन के बारे में और जानने के लिए **जानकारी** टैब देखें।
""",
        "en": """
Welcome to the Plant Disease Recognition System! 🌿🔍

Our mission is to help in identifying plant diseases efficiently. Upload an image of a plant, and our system will analyze it to detect any signs of diseases. Together, let's protect our crops and ensure a healthier harvest!

### How It Works
1. **Upload Image:** Go to the **Disease Recognition** tab above and upload an image of a plant with suspected diseases.
2. **Analysis:** Our system will process the image using advanced algorithms to identify potential diseases.
3. **Results:** View the results and recommendations for further action.

### Why Choose Us?
- **Accuracy:** Trained on 15 crop/disease categories across Pepper, Potato, and Tomato, reaching over 95% accuracy on held-out test data.
- **User-Friendly:** Simple and intuitive interface for seamless user experience.
- **Fast and Efficient:** Receive results in seconds, allowing for quick decision-making.

### Get Started
Click on the **Disease Recognition** tab to upload an image and experience the power of our Plant Disease Recognition System!

### About Us
Learn more about the project, dataset, and model performance on the **About** tab.
""",
    },

    "about_header": {"hi": "हमारे प्रोजेक्ट के बारे में", "en": "About Our Project"},
    "about_body": {
        "hi": """
#### डेटासेट के बारे में
मॉडल को Kaggle के **PlantVillage** डेटासेट ([emmarex/plantdisease](https://www.kaggle.com/datasets/emmarex/plantdisease)) पर प्रशिक्षित किया गया है, जिसमें मिर्च (Pepper), आलू (Potato) और टमाटर (Tomato) की पत्तियों की **20,624 RGB तस्वीरें** हैं, जो **15 फसल/रोग वर्गों** में बंटी हैं। डेटासेट को स्तरीकृत (stratified) 70/15/15 अनुपात में प्रशिक्षण/सत्यापन/परीक्षण सेट में बांटा गया, ताकि सेटों के बीच कोई डेटा लीक न हो।

#### सामग्री
1. प्रशिक्षण (14,436 तस्वीरें — 70%)
2. सत्यापन (3,094 तस्वीरें — 15%)
3. परीक्षण (3,094 तस्वीरें — 15%)

#### मॉडल का प्रदर्शन
प्रशिक्षण नोटबुक में दो मॉडल आज़माए गए — एक कस्टम CNN और EfficientNetB3 (ट्रांसफर लर्निंग)। परीक्षण सेट पर सर्वश्रेष्ठ प्रदर्शन कस्टम CNN का रहा:
- सटीकता (Accuracy): **95.51%**
- संतुलित सटीकता (Balanced Accuracy): **94.86%**
- Macro F1: **94.59%**
- Top-3 सटीकता: **99.81%**
""",
        "en": """
#### About Dataset
The model is trained on Kaggle's **PlantVillage** dataset ([emmarex/plantdisease](https://www.kaggle.com/datasets/emmarex/plantdisease)), consisting of **20,624 RGB images** of Pepper, Potato, and Tomato leaves across **15 crop/disease classes**. The dataset was split into a stratified 70/15/15 train/validation/test set with no overlap between splits.

#### Content
1. train (14,436 images — 70%)
2. validation (3,094 images — 15%)
3. test (3,094 images — 15%)

#### Model Performance
The training notebook evaluated two models — a custom CNN and EfficientNetB3 (transfer learning). The custom CNN was the best performer on the held-out test set:
- Accuracy: **95.51%**
- Balanced Accuracy: **94.86%**
- Macro F1: **94.59%**
- Top-3 Accuracy: **99.81%**
""",
    },
    "about_eyebrow": {"hi": "🌿 15 वर्ग", "en": "🌿 15 Classes"},
    "about_subheader": {"hi": "हर फसल और रोग की सूची", "en": "List of Every Crop with Disease"},
    "table_crop_col": {"hi": "फसल का नाम (Crop)", "en": "Crop"},
    "table_condition_col": {"hi": "रोग/अवस्था (Condition)", "en": "Condition"},
    "table_healthy": {"hi": "स्वस्थ", "en": "Healthy"},

    "predict_header": {"hi": "रोग पहचान", "en": "Disease Recognition"},
    "upload_label": {"hi": "एक तस्वीर अपलोड करें", "en": "Upload an image"},
    "upload_caption": {"hi": "अपलोड की गई तस्वीर", "en": "Uploaded Image"},
    "upload_warning": {"hi": "कृपया जारी रखने के लिए एक तस्वीर अपलोड करें।", "en": "Please upload an image file to continue."},
    "predict_button": {"hi": "पूर्वानुमान लगाएं", "en": "Predict"},
    "prediction_eyebrow": {"hi": "हमारा पूर्वानुमान", "en": "Our Prediction"},
    "predicted_class": {"hi": "पूर्वानुमानित वर्ग", "en": "Predicted Class"},
    "confidence": {"hi": "विश्वास", "en": "Confidence"},
    "plant_healthy": {"hi": "पौधा स्वस्थ है", "en": "The plant appears healthy"},
    "severity_label": {"hi": "गंभीरता (Severity)", "en": "Severity"},

    "prediction_summary_spoken": {
        "hi": "फसल: {crop}. रोग या अवस्था: {condition}. गंभीरता: {severity}.",
        "en": "Crop: {crop}. Condition: {condition}. Severity: {severity}.",
    },
    "listen_prediction_button": {"hi": "🔊 सुनें", "en": "🔊 Listen"},
    "listen_plan_button": {"hi": "🔊 उपचार योजना सुनें", "en": "🔊 Listen to treatment plan"},
    "audio_generating": {"hi": "ऑडियो तैयार किया जा रहा है...", "en": "Generating audio..."},
    "audio_unavailable": {
        "hi": "ऑडियो उपलब्ध नहीं है। कृपया बाद में पुनः प्रयास करें।",
        "en": "Audio isn't available right now. Please try again later.",
    },

    "location_section_header": {"hi": "स्थान-आधारित उपचार योजना", "en": "Location-based Treatment Plan"},
    "location_mode_label": {"hi": "अपना स्थान कैसे देना चाहते हैं?", "en": "How would you like to provide your location?"},
    "location_mode_manual": {"hi": "मैन्युअल रूप से दर्ज करें", "en": "Enter manually"},
    "location_mode_gps": {"hi": "मेरा स्थान उपयोग करें (ब्राउज़र)", "en": "Use my location (browser)"},
    "location_input_label": {"hi": "अपना गाँव/शहर, राज्य दर्ज करें", "en": "Enter your village/city, state"},
    "location_detected": {"hi": "पहचाना गया स्थान: {location}", "en": "Detected location: {location}"},
    "geo_waiting": {
        "hi": "स्थान की अनुमति माँगी जा रही है... कृपया अपने ब्राउज़र में अनुमति दें।",
        "en": "Requesting location permission... please allow it in your browser.",
    },
    "geo_error_0": {"hi": "आपका ब्राउज़र स्थान सेवा का समर्थन नहीं करता।", "en": "Your browser doesn't support location services."},
    "geo_error_1": {
        "hi": "स्थान की अनुमति अस्वीकार कर दी गई। कृपया मैन्युअल रूप से स्थान दर्ज करें।",
        "en": "Location permission was denied. Please enter your location manually.",
    },
    "geo_error_2": {"hi": "स्थान की जानकारी उपलब्ध नहीं है।", "en": "Location information is unavailable."},
    "geo_error_3": {"hi": "स्थान प्राप्त करने का समय समाप्त हो गया।", "en": "Getting your location timed out."},
    "geo_error_default": {
        "hi": "स्थान प्राप्त नहीं हो सका। कृपया मैन्युअल रूप से दर्ज करें।",
        "en": "Couldn't get your location. Please enter it manually.",
    },

    "weather_fetching": {"hi": "मौसम की जानकारी प्राप्त की जा रही है...", "en": "Fetching weather information..."},
    "weather_expander": {
        "hi": "🌦️ मौसम की जानकारी (बीता कल, आज, आने वाला कल)",
        "en": "🌦️ Weather Information (yesterday, today, tomorrow)",
    },

    "get_plan_button": {"hi": "उपचार योजना प्राप्त करें", "en": "Get Treatment Plan"},
    "plan_generating": {"hi": "उपचार योजना तैयार की जा रही है...", "en": "Preparing treatment plan..."},
    "plan_header": {"hi": "स्थान-आधारित उपचार योजना", "en": "Location-based Treatment Plan"},
}


def get_lang():
    return st.session_state.get("lang", "hi")


def t(key, **kwargs):
    entry = _STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(get_lang(), entry.get("hi", key))
    return text.format(**kwargs) if kwargs else text
