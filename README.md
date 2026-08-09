# 🌾 Crop Disease Prediction System

A deep learning web app that identifies plant leaf diseases from a photo, explains what they are, scores how serious they are, and — if you tell it where you're farming — asks an LLM for a treatment plan tailored to your location and the local weather. Built with PyTorch and Streamlit, in Hindi or English.

---

## 📌 Features

- 🔍 **Disease recognition** — a custom ResNet-style CNN classifies uploaded leaf photos into 38 crop/disease classes, with a confidence score.
- 📊 **Facts-based severity** — every disease is scored Low/Medium/High/Critical from real plant-pathology facts (pathogen type, curability, spread rate, yield impact), not model confidence or randomness.
- 📖 **Treatment write-ups** — curated, detailed treatment guidance (cause, symptoms, biological control, chemical control, precautions) for the most common diseases, with a sensible fallback for the rest.
- 📍 **Location-based treatment plans** — share your location (typed in, or via browser geolocation) and a farmer's-context prompt goes to Groq's `llama-3.3-70b-versatile` for a plan with locally-relevant products and timing.
- 🌦️ **Weather-aware advice** — when configured, yesterday/today/tomorrow's weather is pulled in so the plan can account for rain and humidity (e.g. "don't spray today, it's about to rain").
- 🌐 **Hindi / English toggle** — a sidebar switch translates the whole app: every page, severity labels, the treatment write-ups, and the AI-generated plan.
- 🎨 Streamlit UI with a custom design system ("CauseHouse").

---

## 🧠 Model Details

- Framework: PyTorch
- Architecture: custom ResNet-style CNN (`src/custom_resnet.py`), loaded from `models/resnet_Model.pth`
- Image size: `224x224`
- Dataset: [PlantVillage dataset](https://www.kaggle.com/emmarex/plantdisease)
- Classes: 38 total, e.g. `Tomato___Late_blight`, `Potato___Early_blight`, `Apple___Apple_scab`

---

## 🖥️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys (optional, but needed for treatment plans)

```bash
cp .env.example .env
```

Then fill in `.env`:

| Variable | Used for | Get one at |
|---|---|---|
| `GROQ_API_KEY` | Generating location-aware treatment plans | https://console.groq.com/keys |
| `OPENWEATHER_API_KEY` | Yesterday/today/tomorrow weather context | https://openweathermap.org/api |

Both are optional — the app runs fine without either, it just won't offer an AI-generated plan (without `GROQ_API_KEY`) or weather context (without `OPENWEATHER_API_KEY`). Note that weather requires OpenWeatherMap's **"One Call by Call"** subscription (a separate opt-in on their site, even for free-tier usage) — a plain API key alone will get an HTTP 401 on every weather request.

### 3. Run the app

```bash
streamlit run App.py
```

---

## 🧪 How It Works

1. Upload a leaf photo on the **Disease Recognition** page.
2. The model predicts the crop/disease class and a confidence score.
3. Severity is computed from that disease's real-world facts and shown as a color-coded badge.
4. The relevant treatment write-up (or a sensible generic one) is displayed.
5. For diseased (non-healthy) predictions, you can optionally provide your location — typed in, or shared from your browser — to get a location- and weather-aware treatment plan from Groq.
6. Switch the sidebar language toggle at any point to see everything — including the AI-generated plan — in Hindi or English.

---

## 📂 Project Structure

```
cropDisease/
├── App.py                    # Streamlit app: pages, session state, UI flow
├── models/
│   ├── resnet_Model.pth      # Trained custom-ResNet weights (used by App.py)
│   └── crops_cbam_Model.pth  # CBAM-based model (not currently wired into the UI)
├── src/
│   ├── custom_resnet.py      # Model architecture + prediction_img() (class, confidence)
│   ├── Severity.py           # Facts-based severity scoring for all 38 classes
│   ├── Treatment.py          # Hindi treatment write-ups + crop/condition name maps
│   ├── TreatmentEn.py        # English translations of the same write-ups
│   ├── LocationTreatment.py  # Geocoding (Nominatim) + Groq treatment-plan prompt
│   ├── Weather.py            # Yesterday/today/tomorrow weather (OpenWeatherMap)
│   └── i18n.py               # UI string translations + language helper
├── uploads/                  # Sample leaf images used for local testing
├── .env.example               # Template for GROQ_API_KEY / OPENWEATHER_API_KEY (committed, safe)
├── requirements.txt
├── Dockerfile / docker-compose.yml / Procfile / nginx.conf   # Deployment
└── README.md
```

---

## 📚 Dataset Classes

38 classes across 14 crops, e.g.:

```python
['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
 'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
 'Tomato___Leaf_Mold', 'Tomato___Late_blight', ..., 'Tomato___Tomato_Yellow_Leaf_Curl_Virus']
```

The full list — with severity — is in `src/Severity.py`; the full list with Hindi/English names is browsable on the app's **About** page.

---

## 🙏 Acknowledgements

- [PlantVillage Dataset](https://www.kaggle.com/emmarex/plantdisease)
- [Streamlit](https://streamlit.io/)
- [Groq](https://groq.com/) for LLM inference
- [OpenWeatherMap](https://openweathermap.org/) for weather data
- [OpenStreetMap Nominatim](https://nominatim.org/) for geocoding
