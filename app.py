"""Local dashboard for trained flow classification and experiment evidence."""
from pathlib import Path
import json
import pandas as pd
import streamlit as st
import torch
from nids.inference import Predictor
from nids.schema import CLASSES, FEATURE_INFO, FEATURES

ROOT = Path(__file__).resolve().parent
torch.set_num_threads(4)
st.set_page_config(page_title="FlowGuard | Transformer NIDS", page_icon="🛡️", layout="wide")
st.markdown("""<style>
.stApp {background:#f5f7fb;}
div[data-testid="stMetric"] {background:white;border:1px solid #e2e8f0;padding:18px;border-radius:14px;}
.hero {background:linear-gradient(115deg,#0d172a,#173967);padding:32px 36px;border-radius:18px;color:white;margin-bottom:24px;}
.hero h1 {color:white;font-size:38px;margin:4px 0 10px;}
.hero p {color:#d3e2f5;max-width:920px;line-height:1.6;}
.eyebrow {font-size:12px;letter-spacing:2px;color:#90c3ff;font-weight:700;}
.stTabs [data-baseweb="tab-list"] {gap:22px;}
</style>""", unsafe_allow_html=True)
st.markdown("""<div class="hero"><div class="eyebrow">COMPUTER NETWORKS · MULTI-CLASS INTRUSION DETECTION</div>
<h1>FlowGuard</h1><p>Transformer-based network intrusion detection. Inspect completed network flows,
classify network attacks, and explore measured model performance.</p></div>""", unsafe_allow_html=True)

profile=st.sidebar.radio('Classifier profile',['Core five classes','Extended seven classes'])
extended=profile=='Extended seven classes'
if st.session_state.get('active_profile')!=profile:
    st.session_state.pop('result',None);st.session_state.pop('analyzed_frame',None)
    st.session_state['active_profile']=profile
artifact_root=ROOT/'artifacts/extended' if extended else ROOT/'artifacts'
data_root=ROOT/'data/extended' if extended else ROOT/'data'
result_root=ROOT/'results/extended' if extended else ROOT/'results'


@st.cache_resource
def get_predictor(path):
    return Predictor(path)


try:
    predictor = get_predictor(str(artifact_root))
except (FileNotFoundError, RuntimeError, ValueError) as error:
    st.error(f"Trained model could not be loaded: {error}")
    st.info("Follow README.md to prepare data and run scripts/train.py. The dashboard never trains a model automatically.")
    st.stop()

metadata = predictor.metadata
CLASSES=predictor.classes
metrics_path = result_root / "test_metrics.json"
metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
with st.sidebar:
    st.title("🛡️ FlowGuard")
    st.caption("LOCAL RESEARCH PROTOTYPE")
    st.success("Trained Transformer loaded")
    st.markdown("**Traffic classes**")
    for cls in CLASSES:
        st.write("• " + cls)
    st.divider()
    st.write(f"**{len(FEATURES)}** numeric flow features")
    st.write("**2** encoder layers · **4** attention heads")
    st.caption("CSV inference runs locally. Predictions use a closed set of classes; probability scores are not calibrated confidence.")

detect, performance, architecture, lab, guide = st.tabs(["Analyze flows", "Model performance", "How it works", "Extended lab", "Project guide"])
with detect:
    st.subheader("Analyze a network-flow CSV")
    st.caption("Use CIC-IDS2017/CICFlowMeter-compatible feature names and units. Raw packet captures need a separate feature extractor.")
    left, right = st.columns([2,1])
    with left:
        mode = st.radio("Input source", ["Included held-out examples", "Upload CSV"], horizontal=True)
        if mode == "Included held-out examples":
            frame = pd.read_csv(data_root / "samples/demo_flows.csv")
            st.info(f"{len(frame)} held-out dataset flows, up to 10 per actual class. Predictions may be incorrect.")
        else:
            uploaded = st.file_uploader("Choose CSV", type=["csv"])
            frame = None
            if uploaded:
                try:
                    frame = pd.read_csv(uploaded, nrows=25001)
                    if len(frame) > 25000:
                        st.error("Use at most 25,000 flows per upload; use the CLI for larger files.")
                        frame = None
                except Exception as error:
                    st.error(f"Could not read CSV: {error}")
    with right:
        st.markdown("**Try the sample**")
        st.download_button("Download example CSV", (data_root / "samples/demo_flows.csv").read_bytes(),
                           "demo_flows.csv", "text/csv", width="stretch")
        st.caption("Labels and identifiers are not required for prediction. Missing numeric cells use training medians.")
    if frame is not None:
        with st.expander("Preview input features", expanded=False):
            st.dataframe(frame.head(10), width="stretch")
        if st.button("Classify flows", type="primary", width="stretch"):
            try:
                with st.spinner("Running the Transformer..."):
                    result = predictor.predict(frame)
                st.session_state["result"] = result
                st.session_state["analyzed_frame"] = frame.copy()
            except ValueError as error:
                st.error(str(error))
    result = st.session_state.get("result")
    if result is not None:
        st.divider()
        st.caption("Results below belong to the most recently classified input.")
        cols = st.columns(4)
        cols[0].metric("Flows analyzed", f"{len(result):,}")
        cols[1].metric("Predicted attacks", f"{result.is_attack.sum():,}")
        cols[2].metric("Predicted benign", f"{(~result.is_attack).sum():,}")
        cols[3].metric("Attack share", f"{result.is_attack.mean():.1%}")
        c1, c2 = st.columns([1,2])
        with c1:
            st.markdown("**Predicted traffic distribution**")
            counts = result.predicted_class.value_counts().reindex(CLASSES, fill_value=0)
            st.bar_chart(counts, color="#2563eb")
        with c2:
            st.markdown("**Flow predictions**")
            chosen = st.multiselect("Show classes", CLASSES, default=CLASSES)
            st.dataframe(result[result.predicted_class.isin(chosen)], width="stretch", hide_index=True)
        st.download_button("Download all predictions", result.to_csv(index=False), "flow_predictions.csv", "text/csv")
        with st.expander("Explore feature sensitivity for one flow"):
            st.caption("One-feature-at-a-time median replacement. Positive drop means replacing that feature reduced the predicted-class probability. This is a sensitivity probe, not SHAP, LIME, or causal attribution.")
            number = st.number_input("Flow number", min_value=1, max_value=len(result), value=1)
            if st.button("Explain selected flow"):
                explanation = predictor.occlusion_explanation(st.session_state["analyzed_frame"].iloc[[number-1]])
                st.write("Predicted class: **" + result.iloc[number-1].predicted_class + "**")
                st.dataframe(explanation, hide_index=True, width="stretch")

with performance:
    st.subheader("Measured evaluation")
    st.caption("CIC-IDS2017 public-mirror subset · unique feature-vector stratified random split · one seed/configuration per model")
    if "Transformer" in metrics:
        tm = metrics["Transformer"]
        cols = st.columns(4)
        cols[0].metric("Transformer accuracy", f"{tm['accuracy']:.2%}")
        cols[1].metric("Macro-F1", f"{tm['macro_f1']:.4f}")
        cols[2].metric("Benign false-positive rate", f"{tm['benign_false_positive_rate']:.2%}")
        cols[3].metric("Model inference / flow", f"{tm['inference_ms_per_flow']:.3f} ms")
        st.caption("Inference timing excludes capture, feature extraction, and preprocessing; it is a batched CPU measurement.")
        st.dataframe(pd.read_csv(result_root / "model_comparison.csv"), width="stretch", hide_index=True)
        st.image(str(result_root / "plots/model_comparison.png"))
        name = st.selectbox("Inspect model confusion matrix", list(metrics))
        c1, c2 = st.columns(2)
        with c1:
            st.image(str(result_root / f"plots/{name}_confusion.png"))
        with c2:
            report = metrics[name]["classification_report"]
            st.dataframe(pd.DataFrame({c: report[c] for c in CLASSES}).T, width="stretch")
        st.image(str(result_root / "plots/learning_curves.png"))
    st.warning("Random-split benchmark results can be optimistic because related sessions remain. These measurements do not establish zero-day detection or live-network reliability.")

with architecture:
    st.subheader("From flow features to attack classification")
    st.code("Completed network flow\n  → 24 CICFlowMeter-compatible statistics\n  → training-median imputation\n  → signed log transform + training standardization\n  → feature-value embeddings + feature identities + CLS token\n  → 2 Transformer encoder layers / 4 heads\n  → CLS representation + five-class head\n  → prediction probabilities", language="text")
    st.write("This classifier connects features within one flow. The Extended lab contains a separate chronological Temporal Transformer, contextual tabular encoder, flow-grid ViT, graph model and adaptation experiments.")
    st.dataframe(pd.DataFrame(FEATURE_INFO, columns=["Feature", "Unit", "Meaning"]), hide_index=True, width="stretch")
    with st.expander("Model and environment configuration"):
        st.json(metadata)

with lab:
    st.subheader('Temporal, graph and alternative models')
    advanced_path=ROOT/'artifacts/advanced/model_metadata.json'
    if advanced_path.exists():
        advanced_meta=json.loads(advanced_path.read_text())
        choice=st.selectbox('Advanced model',list(advanced_meta['models']))
        st.caption('Context inputs include source/destination IPs, ports, protocol and a flag-derived state. Temporal predictions label the last flow of each complete chronological 8-flow window; partial windows produce no prediction.')
        source=st.radio('Advanced input',['Included chronological test flows','Upload context CSV'])
        incoming=None
        if source=='Included chronological test flows':incoming=pd.read_csv(ROOT/'data/temporal/test_flows.csv')
        else:
            uploaded_context=st.file_uploader('Context flow CSV',type=['csv'],key='context_upload')
            if uploaded_context:
                incoming=pd.read_csv(uploaded_context,nrows=5001)
                if len(incoming)>5000:st.error('Use at most 5,000 context flows');incoming=None
        if incoming is not None and st.button('Run advanced model'):
            from nids.advanced_inference import AdvancedPredictor
            try:
                with st.spinner('Predicting with '+choice):output=AdvancedPredictor(ROOT/'artifacts/advanced',choice).predict(incoming)
                st.dataframe(output,width='stretch',hide_index=True)
                st.download_button('Download advanced predictions',output.to_csv(index=False),'advanced_predictions.csv','text/csv')
            except (ValueError,KeyError) as error:st.error(str(error))
        st.dataframe(pd.read_csv(ROOT/'results/advanced/model_comparison.csv'),width='stretch',hide_index=True)
        st.caption('Temporal and individual-flow evaluation use different output rows. FedAvg is a local three-client simulation; online updates require observed labels.')
    else:st.info('Advanced training is in progress. Models appear here after artifacts are saved.')
    st.divider();st.subheader('SHAP and LIME explanations')
    method=st.selectbox('Explanation method',['SHAP','LIME'])
    if st.button('Explain first sample with '+method):
        from nids.explain import explain_shap,explain_lime
        background=pd.read_csv(data_root/'processed/train_flows.csv').sample(100,random_state=42)
        sample=pd.read_csv(data_root/'samples/demo_flows.csv').iloc[[0]]
        medians=pd.Series(predictor.preprocessor.named_steps['impute'].statistics_,index=FEATURES)
        try:
            with st.spinner('Computing '+method):
                table,detail=(explain_shap if method=='SHAP' else explain_lime)(predictor,background.fillna(medians),sample.fillna(medians))
            st.json(detail);st.dataframe(table,width='stretch',hide_index=True)
        except ImportError:st.error('Install requirements-extensions.txt to enable SHAP/LIME')
    st.divider();st.subheader('Passive capture and PCAP replay')
    st.code('python scripts/monitor.py --pcap data/samples/synthetic_pipeline_demo.pcap\npython scripts/monitor.py --list-interfaces\npython scripts/monitor.py --interface "YOUR_INTERFACE" --seconds 60',language='powershell')
    st.caption('Windows live capture needs Npcap and capture permissions. PCAP replay is tested. The custom extractor differs from CICFlowMeter; live accuracy is not established.')
    if (ROOT/'results/pcap_replay.summary.json').exists():st.json(json.loads((ROOT/'results/pcap_replay.summary.json').read_text()))

with guide:
    st.subheader("Project package")
    st.write("The package contains source code, saved models, processed split data, sample flows, experiment metrics, confusion matrices, report, presentation, and viva notes.")
    st.markdown("""1. Use the included sample to demonstrate classification.
2. Inspect comparison metrics and per-class errors.
3. Read `docs/PROJECT_REPORT.md` for the methodology and measured findings.
4. Open `docs/PRESENTATION.html` for the presentation.
5. Follow `README.md` to reproduce training or predict a new CSV.""")
    st.caption("Use matching flow-extraction semantics for new data. This application analyzes flows and does not block traffic.")

