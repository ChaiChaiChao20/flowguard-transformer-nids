"""Exercise the actual Streamlit app against the supplied trained checkpoint."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless((ROOT / "artifacts/model_metadata.json").exists(), "Requires trained project artifacts")
class DashboardTests(unittest.TestCase):
    def test_extended_profile_temporal_and_shap(self):
        from streamlit.testing.v1 import AppTest
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run()
        next(r for r in app.radio if r.label=='Classifier profile').set_value('Extended seven classes').run()
        next(b for b in app.button if b.label=='Classify flows').click().run()
        self.assertEqual(len(app.exception),0,str(app.exception))
        self.assertEqual(next(m for m in app.metric if m.label=='Flows analyzed').value,'65')
        next(s for s in app.selectbox if s.label=='Advanced model').set_value('TemporalTransformer').run()
        next(b for b in app.button if b.label=='Run advanced model').click().run()
        self.assertEqual(len(app.exception),0,str(app.exception))
        outputs=[d.value for d in app.dataframe if 'input_row' in d.value.columns]
        self.assertEqual(len(outputs[0]),196)
        next(b for b in app.button if b.label=='Explain first sample with SHAP').click().run()
        self.assertEqual(len(app.exception),0,str(app.exception))
        self.assertTrue(any('shap_value' in d.value.columns for d in app.dataframe))

    def test_sample_classification_and_sensitivity(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
        self.assertEqual(len(app.exception), 0, str(app.exception))
        next(button for button in app.button if button.label == "Classify flows").click().run()
        self.assertEqual(len(app.exception), 0, str(app.exception))
        metric = next(m for m in app.metric if m.label == "Flows analyzed")
        self.assertEqual(metric.value, "50")
        next(button for button in app.button if button.label == "Explain selected flow").click().run()
        self.assertEqual(len(app.exception), 0, str(app.exception))
        self.assertTrue(any("Predicted class:" in block.value for block in app.markdown))


if __name__ == "__main__":
    unittest.main()
