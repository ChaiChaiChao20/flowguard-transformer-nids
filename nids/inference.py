"""Shared batch prediction for CLI, evaluation, and dashboard."""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import torch
from .models import build_model
from .preprocessing import numeric_features


class Predictor:
    def __init__(self, artifacts):
        self.root = Path(artifacts)
        self.metadata = json.loads((self.root / "model_metadata.json").read_text(encoding="utf-8"))
        self.classes = self.metadata["classes"]
        self.preprocessor = joblib.load(self.root / "preprocessor.joblib")
        self.model = build_model("Transformer", len(self.metadata["features"]), len(self.classes), **self.metadata["transformer_config"])
        self.model.load_state_dict(torch.load(self.root / "Transformer.pt", map_location="cpu", weights_only=True))
        self.model.eval()
        self.anomaly=joblib.load(self.root/'anomaly.joblib') if (self.root/'anomaly.joblib').exists() else None

    def probabilities(self, frame, batch_size=256):
        values = numeric_features(frame, strict=True)
        x = self.preprocessor.transform(values).astype("float32")
        if not np.isfinite(x).all():
            raise ValueError("Preprocessing produced invalid values; inspect the input ranges.")
        with torch.inference_mode():
            return np.concatenate([torch.softmax(self.model(torch.from_numpy(x[i:i+batch_size])), dim=1).numpy()
                                   for i in range(0, len(x), batch_size)])

    def predict(self, frame):
        probs = self.probabilities(frame)
        indices = probs.argmax(axis=1)
        result = pd.DataFrame({"flow_number": np.arange(1, len(frame)+1),
                               "predicted_class": np.array(self.classes)[indices],
                               "model_probability": probs.max(axis=1),
                               "is_attack": indices != self.classes.index("Benign")})
        for i, cls in enumerate(self.classes):
            result[f"probability_{cls.replace(' ', '_')}"] = probs[:, i]
        if self.anomaly is not None:
            x=self.preprocessor.transform(numeric_features(frame,strict=True)).astype('float32')
            scores=-self.anomaly['model'].score_samples(x)
            result['anomaly_score']=scores
            result['atypical_flag']=scores>self.anomaly['threshold']
        return result

    def occlusion_explanation(self, row):
        """Replace one feature at a time with its training median; not SHAP/LIME."""
        raw = numeric_features(row.iloc[:1], strict=True)
        original = self.probabilities(raw)[0]
        predicted = int(original.argmax())
        perturbed = pd.concat([raw] * len(raw.columns), ignore_index=True)
        for i, feature in enumerate(raw.columns):
            perturbed.loc[i, feature] = self.preprocessor.named_steps["impute"].statistics_[i]
        changed = self.probabilities(perturbed)[:, predicted]
        return pd.DataFrame({"feature": raw.columns,
                             "probability_drop": original[predicted] - changed}).sort_values("probability_drop", ascending=False)
