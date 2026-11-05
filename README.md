# Crop Disease Detection

A Streamlit app that diagnoses plant diseases from a photo of a leaf and tells the farmer what to do about it, in Hindi or English.

Upload a leaf image and the app:

1. **Classifies it** into one of 38 PlantVillage classes (14 crops, healthy or diseased) with a custom ResNet-style CNN in PyTorch, and shows the confidence.
2. **Scores severity** from plant-pathology facts about that disease (pathogen type, curability, spread rate, yield impact), not from model confidence, so a given disease always gets the same severity.
3. **Shows treatment guidance** from a curated table, in Hindi or English.
4. **Builds a location-aware treatment plan** (optional). It takes your location from browser geolocation or a typed place name, pulls yesterday/today/tomorrow weather from Open-Meteo, and asks an LLM on Groq (Llama 3.3 70B) for advice suited to the local climate, products and timing.
5. **Reads the result aloud** with gTTS, which works even on devices without a Hindi voice installed.

The whole interface switches between Hindi and English from the sidebar.

## Run it

Python 3.11 recommended.

```bash
git clone https://github.com/devSaksham/crop-disease-detection.git
cd crop-disease-detection
pip install -r requirements.txt
cp .env.example .env      # add GROQ_API_KEY to enable location-aware plans
streamlit run App.py
```

Diagnosis, severity, built-in treatment and speech all work without a key; only the LLM treatment plan needs `GROQ_API_KEY`. Geocoding (Nominatim) and weather (Open-Meteo) are keyless. Sample leaf images to try are in `uploads/`.

The repo also has a dev container: open it in GitHub Codespaces and the app starts on port 8501.

## Model

`models/resnet_Model.pth` (~26 MB) is a ResNet-9-style CNN: four conv blocks (64→128→256→512) with two residual blocks, then global average pooling and a 38-way linear layer. Inputs are resized to 224×224. The training notebook is `notebooks/train_custom_resnet_pytorch.ipynb`, which also includes a CBAM-attention variant.

`notebooks/plantvillage_cnn_vs_efficientnet_keras.ipynb` is a separate Keras study on a 15-class PlantVillage subset. It compares a VGG-style CNN against EfficientNetB3 transfer learning with class weights, balanced accuracy and macro-F1, then exports to `.keras`, `.h5` and TFLite with a check that the exports agree.

## Layout

```
App.py                      Streamlit UI: tabs, upload, results, location flow
src/
  custom_resnet.py          model definition, loading, prediction
  Severity.py               facts-based severity for all 38 classes
  Treatment.py, TreatmentEn.py   treatment text (Hindi / English)
  LocationTreatment.py      geocoding + Groq LLM treatment plan
  Weather.py                Open-Meteo 3-day context
  Speech.py                 gTTS text-to-speech
  i18n.py                   UI strings in Hindi and English
models/resnet_Model.pth     trained weights
notebooks/                  training and benchmarking notebooks
uploads/                    sample leaf images
presentation/               project slides
```

## Dataset

[PlantVillage](https://www.kaggle.com/datasets/emmarex/plantdisease): leaf images across 38 crop-disease classes.
