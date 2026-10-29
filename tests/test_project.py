"""Checks focused on leakage, input handling, and trained artifact parity."""
import json
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
import torch
from nids.preprocessing import build_preprocessor, numeric_features
from nids.models import build_model
from nids.schema import CLASSES, FEATURES

ROOT = Path(__file__).resolve().parents[1]


class InputContractTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame(np.arange(3*len(FEATURES)).reshape(3,-1), columns=FEATURES)

    def test_reorders_columns_and_ignores_label(self):
        other = self.frame[FEATURES[::-1]].copy()
        other["Label"] = "DDoS"
        pd.testing.assert_frame_equal(numeric_features(other), numeric_features(self.frame))

    def test_missing_column_rejected(self):
        with self.assertRaisesRegex(ValueError, "Missing required"):
            numeric_features(self.frame.drop(columns=FEATURES[0]), strict=True)

    def test_string_and_all_missing_row_rejected(self):
        broken = self.frame.astype(object)
        broken.loc[0, FEATURES[0]] = "invalid"
        with self.assertRaisesRegex(ValueError, "Non-numeric"):
            numeric_features(broken, strict=True)
        with self.assertRaisesRegex(ValueError, "no usable"):
            numeric_features(pd.DataFrame([[np.nan]*len(FEATURES)], columns=FEATURES), strict=True)

    def test_imputer_does_not_refit_on_new_inputs(self):
        pre = build_preprocessor().fit(self.frame)
        before = pre.named_steps["impute"].statistics_.copy()
        incoming = self.frame.astype(float).copy()
        incoming.loc[0, FEATURES[0]] = np.nan
        self.assertTrue(np.isfinite(pre.transform(incoming)).all())
        np.testing.assert_array_equal(before, pre.named_steps["impute"].statistics_)

    def test_models_output_all_classes(self):
        torch.set_num_threads(2)
        for name in ["Transformer", "MLP", "CNN", "LSTM", "GRU"]:
            with self.subTest(model=name):
                model = build_model(name, len(FEATURES), len(CLASSES)).eval()
                with torch.inference_mode():
                    logits = model(torch.zeros(3, len(FEATURES)))
                self.assertEqual(tuple(logits.shape), (3, len(CLASSES)))


@unittest.skipUnless((ROOT / "data/processed/split_manifest.csv").exists(), "Requires prepared data")
class DataIntegrityTests(unittest.TestCase):
    def test_no_feature_hash_overlap_or_conflicting_labels(self):
        manifest = pd.read_csv(ROOT / "data/processed/split_manifest.csv", dtype={"feature_hash": "string"})
        self.assertFalse(manifest.feature_hash.duplicated().any())
        self.assertEqual(set(manifest.split), {"train", "validation", "test"})
        for split, part in manifest.groupby("split"):
            self.assertEqual(set(part.target), set(CLASSES), split)

    def test_preprocessor_is_fit_only_on_training_medians(self):
        import joblib
        raw = pd.read_csv(ROOT / "data/processed/train_flows.csv")
        pre = joblib.load(ROOT / "data/processed/preprocessor.joblib")
        expected = numeric_features(raw).median().fillna(0).to_numpy()
        np.testing.assert_allclose(pre.named_steps["impute"].statistics_, expected)


@unittest.skipUnless((ROOT / "artifacts/model_metadata.json").exists(), "Requires trained model")
class ArtifactParityTests(unittest.TestCase):
    def test_fresh_loading_and_inference_matches_evaluation(self):
        from nids.inference import Predictor
        raw = pd.read_csv(ROOT / "data/processed/test_flows.csv")
        recorded = pd.read_csv(ROOT / "results/Transformer_test_predictions.csv")
        predictor = Predictor(ROOT / "artifacts")
        result = predictor.predict(raw)
        self.assertEqual(result.predicted_class.tolist(), recorded.predicted_class.tolist())
        np.testing.assert_allclose(result.model_probability, recorded.model_probability, rtol=1e-5, atol=1e-6)
        shuffled = raw[FEATURES[::-1]].iloc[:7]
        np.testing.assert_allclose(predictor.probabilities(shuffled), predictor.probabilities(raw.iloc[:7]), atol=1e-6)
        np.testing.assert_allclose(predictor.probabilities(raw.iloc[:7]).sum(1), 1, atol=1e-6)

    def test_occlusion_explanation_is_finite(self):
        from nids.inference import Predictor
        raw = pd.read_csv(ROOT / "data/samples/demo_flows.csv").iloc[:1]
        explanation = Predictor(ROOT / "artifacts").occlusion_explanation(raw)
        self.assertEqual(set(explanation.feature), set(FEATURES))
        self.assertTrue(np.isfinite(explanation.probability_drop).all())


if __name__ == "__main__":
    unittest.main()
