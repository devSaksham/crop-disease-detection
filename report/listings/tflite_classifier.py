class TFLitePlantClassifier:
    """Deployment-shaped wrapper -- mirrors what a mobile/server client does."""
    def __init__(self, model_path, labels_path=None):
        self.interp = tf.lite.Interpreter(model_path=str(model_path))
        self.interp.allocate_tensors()
        self.inp = self.interp.get_input_details()[0]
        self.out = self.interp.get_output_details()[0]
        self.size = self.inp["shape"][1]
        self.labels = (Path(labels_path).read_text().splitlines() if labels_path else CLASSES)

    def predict(self, img_path, topk=3):
        img = np.array(Image.open(img_path).convert("RGB").resize((self.size, self.size)),
                       dtype=np.float32)[None]
        self.interp.set_tensor(self.inp["index"], img)
        self.interp.invoke()
        p = self.interp.get_tensor(self.out["index"])[0]
        idx = p.argsort()[::-1][:topk]
        return [{"label": self.labels[i], "readable": prettify(self.labels[i]),
                 "confidence": round(float(p[i]), 4)} for i in idx]

# Usage:
#   clf = TFLitePlantClassifier("custom_cnn_plantvillage_fp16.tflite", "labels.txt")
#   clf.predict("leaf.jpg", topk=3)
#   -> [{"label": ..., "readable": ..., "confidence": ...}, ...]
