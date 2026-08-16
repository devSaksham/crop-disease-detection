
# 🌾 Crop Disease Prediction Using PyTorch and Streamlit

This project is a deep learning-based web application for identifying plant leaf diseases using PyTorch as the backend framework and Streamlit as the frontend UI. It helps farmers, agronomists, and researchers detect crop diseases quickly and take early action.

---

## 📌 Features

- 🔍 Image classification using a trained CNN (Convolutional Neural Network).
- 🌿 Support for multiple plant species and disease classes.
- 📈 High accuracy using a custom-trained model on PlantVillage/Sea Animals/Crop-specific datasets.
- 🖼️ Simple drag-and-drop interface to upload images.
- 🧪 Displays prediction results with treatment info in **Hindi** or English.
- 🌐 Web-based interface using **Streamlit**.

---

## 🧠 Model Details

- Framework: PyTorch
- Architecture: Custom CNN, benchmarked against EfficientNet during training — the custom CNN came out on top on macro-F1, so the app is built around it
- Image Size:  `224x224` (adjusted per model)
- Dataset: [PlantVillage dataset](https://www.kaggle.com/emmarex/plantdisease), custom-annotated crop dataset
- Classes: Total 38 Classes e.g. `Tomato___Late_blight`, `Potato___Early_blight`, `Apple___Scab`, etc.

---

## 🖥️ Installation

### 🔧 Requirements

```bash
pip install -r requirements.txt
```

Typical dependencies include:
```text
torch
torchvision
streamlit
Pillow
numpy
matplotlib

```

---

## 🚀 How to Run

### Run the Streamlit App:

```bash
.streamlit run App.py
```

### Project Structure:

```
CropDiseasePrediction/
├── App.py                 # Streamlit frontend
├── model/
│   ├── best_model.pt      # Trained PyTorch model
│   
├── dataset/
│   └── test_image.jpg     # Sample test images
├── utils/
│   └── predict.py         # Prediction utilities
├── treatment_info/
│   └── treatment.py  # हिंदी उपचार निर्देश
├── README.md
└── requirements.txt
```

---

## 🧪 How It Works

1. User uploads a leaf image through the Streamlit web app.
2. The image is preprocessed (resized, normalized).
3. The model classifies the image into one of the predefined classes.
4. Displays:
   - Predicted class
   - Confidence score
   - Recommended **treatment in Hindi** or English

---

## 🌱 Example Output

| Input Image | Predicted Class | Treatment |
|-------------|-----------------|-----------|
| Tomato leaf | Tomato___Late_blight | हर 7 दिन के अंतराल पर मैनकोज़ेब का छिड़काव करें |

---

## 📚 Dataset Classes

```python
['Apple___Apple_scab', 'Potato___Late_blight', 'Tomato___Leaf_Mold', ..., 'Tomato___Tomato_Yellow_Leaf_Curl_Virus']
```


## 🙏 Acknowledgements

- [PlantVillage Dataset](https://www.kaggle.com/emmarex/plantdisease)
- Custom CNN architecture
- [Streamlit](https://streamlit.io/)
