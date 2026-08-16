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
- **सटीकता:** सटीक रोग पहचान के लिए अत्याधुनिक मशीन लर्निंग तकनीकों का उपयोग।
- **उपयोग में आसान:** सहज और सरल इंटरफ़ेस।
- **तेज़ और कुशल:** कुछ ही सेकंड में परिणाम, तुरंत निर्णय लेने में मदद।

### शुरू करें
ऊपर **रोग पहचान** टैब पर क्लिक करें और अपने पौधों के लिए हमारी प्रणाली का लाभ उठाएं!

### हमारे बारे में
प्रोजेक्ट, हमारी टीम और हमारे लक्ष्यों के बारे में और जानने के लिए **जानकारी** टैब देखें।
""",
        "en": """
Welcome to the Plant Disease Recognition System! 🌿🔍

Our mission is to help in identifying plant diseases efficiently. Upload an image of a plant, and our system will analyze it to detect any signs of diseases. Together, let's protect our crops and ensure a healthier harvest!

### How It Works
1. **Upload Image:** Go to the **Disease Recognition** tab above and upload an image of a plant with suspected diseases.
2. **Analysis:** Our system will process the image using advanced algorithms to identify potential diseases.
3. **Results:** View the results and recommendations for further action.

### Why Choose Us?
- **Accuracy:** Our system utilizes state-of-the-art machine learning techniques for accurate disease detection.
- **User-Friendly:** Simple and intuitive interface for seamless user experience.
- **Fast and Efficient:** Receive results in seconds, allowing for quick decision-making.

### Get Started
Click on the **Disease Recognition** tab to upload an image and experience the power of our Plant Disease Recognition System!

### About Us
Learn more about the project, our team, and our goals on the **About** tab.
""",
    },

    "about_header": {"hi": "हमारे प्रोजेक्ट के बारे में", "en": "About Our Project"},
    "about_body": {
        "hi": """
#### डेटासेट के बारे में
यह डेटासेट मूल डेटासेट से ऑफ़लाइन ऑगमेंटेशन के माध्यम से बनाया गया है। मूल डेटासेट इस GitHub रिपॉज़िटरी पर उपलब्ध है।
इस डेटासेट में स्वस्थ और रोगग्रस्त फसल पत्तियों की लगभग 87 हज़ार RGB तस्वीरें हैं, जिन्हें 38 अलग-अलग वर्गों में बांटा गया है। पूरे डेटासेट को 80/20 अनुपात में प्रशिक्षण और सत्यापन सेट में विभाजित किया गया है, जिसमें डायरेक्टरी संरचना बनाए रखी गई है।
पूर्वानुमान के लिए बाद में 33 परीक्षण तस्वीरों वाली एक नई डायरेक्टरी बनाई गई।
#### सामग्री
1. प्रशिक्षण (70,295 तस्वीरें)
2. परीक्षण (33 तस्वीरें)
3. सत्यापन (17,572 तस्वीरें)
""",
        "en": """
#### About Dataset
This dataset is recreated using offline augmentation from the original dataset. The original dataset can be found on this GitHub repo.
This dataset consists of about 87K RGB images of healthy and diseased crop leaves which is categorized into 38 different classes. The total dataset is divided into 80/20 ratio of training and validation set preserving the directory structure.
A new directory containing 33 test images is created later for prediction purpose.
#### Content
1. train (70295 images)
2. test (33 images)
3. validation (17572 images)
""",
    },
    "about_eyebrow": {"hi": "🌿 38 वर्ग", "en": "🌿 38 Classes"},
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

    "plan_disclaimer": {
        "hi": "⚠️ यह उपचार योजना AI-जनित मार्गदर्शन मात्र है। कोई भी रासायनिक उपचार लागू करने से पहले स्थानीय कृषि अधिकारी या विशेषज्ञ से सलाह लें।",
        "en": "⚠️ This treatment plan is AI-generated guidance only. Consult a local agriculture officer or expert before applying any chemical treatment.",
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
