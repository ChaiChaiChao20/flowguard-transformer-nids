# Read this first: teammate / Codex handoff

Prepared 19 October 2026. Project: **Transformer-Based Network Intrusion Detection System for Intelligent Multi-Class Cyber Attack Classification**. Product/demo name: **FlowGuard**.

## Open on another computer

1. Extract the full ZIP to a short folder such as `C:\Projects\Transformer_NIDS`.
2. Install Python 3.12. Do not copy the original developer's Python environment.
3. Open PowerShell in the extracted project folder and run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\SETUP_PROJECT.ps1
.\.venv\Scripts\python.exe -m streamlit run app.py
```

After setup, double-click `OPEN_PROJECT.cmd` for subsequent launches. Keep the server terminal open. Open the URL printed by Streamlit, at **http://127.0.0.1:8502**.

On macOS/Linux:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-extensions.txt
.venv/bin/python -m streamlit run app.py
```

Internet is needed for initial dependency installation. The supplied saved models and sample data allow a demo without training or downloading raw datasets. requirements-lock.txt records the original tested Windows environment; requirements-extensions.txt is the normal portable installation entry point. Installation on the teammate's computer has not yet been verified.

## Website link: local versus public

- Original computer's current local URL: `http://127.0.0.1:8502` while its server runs.
- Teammate's usual URL after their own launch: `http://127.0.0.1:8502` (or the URL printed in their terminal).
- **There is no public hosted URL in this package.** Localhost always refers to the computer opening the link. The original localhost link cannot show this dashboard on a teammate's different computer.
- A permanent shared URL requires a separate deployment. The current configuration deliberately binds locally. Do not expose a development server by changing firewall/network settings as a substitute for deployment.

## Continue in Codex

Open the extracted folder as a project in the teammate's Codex. Paste this prompt:

> Continue this existing FlowGuard project. First read CODEX_HANDOFF.md, README.md, docs/REQUIREMENT_TRACEABILITY.md and docs/COMPLETE_PROJECT_GUIDE.md. Inspect the existing code, saved checkpoints, data manifests and results before editing. Set up the local Python environment, run the dashboard and verify the existing tests. Preserve the measured results and distinguish core feature classification, chronological experiments, simulations and unverified deployment claims. Do not retrain or overwrite reference artifacts unless needed for the requested change; use separate output folders for new experiments. Then help me implement my next requested change.

The previous chat and original Python environment do not travel with the ZIP. This handoff file, source, artifacts, data manifests, results and documents provide the continuation context.

## What has been built

- Trained five-class and seven-class feature Transformers. Seven traffic labels: Benign, DoS, DDoS, Botnet, Port Scan, Brute Force and Infiltration.
- Seven-model feature comparisons: Logistic Regression, Random Forest, MLP, CNN, LSTM, GRU and Transformer.
- Context experiments: BERT-style scratch-trained feature encoder, TabTransformer, flow-grid ViT, shared-endpoint GCN and causal Temporal Transformer.
- Three-client local FedAvg simulation, supervised prequential online-learning experiment and Page-Hinkley loss-change detector.
- Actual SHAP KernelExplainer, LIME Tabular, median-replacement sensitivity and benign-trained anomaly scores.
- Passive IPv4 TCP/UDP flow aggregation, PCAP replay, interface-capture code and JSONL events.
- Streamlit dashboard: profile selector, CSV analysis, predictions/export, performance, Extended lab and explainability.
- Saved checkpoints, preprocessors, sampled splits, provenance, predictions, metrics, plots, notebook, report, editable PPT, viva guide and three-person presentation guide.

## Important files

| Path | Purpose |
|---|---|
| app.py | Dashboard entry point |
| nids/schema.py, preprocessing.py, models.py, inference.py | Feature classifier and input contract |
| nids/context.py, advanced_models.py, advanced_inference.py | Network context, temporal/alternative models and inference |
| nids/adaptation.py, explain.py, capture.py | Adaptation, explanations and packet aggregation |
| scripts/download_data.py, download_temporal.py | Pinned data downloads |
| scripts/prepare_data.py, prepare_temporal.py | Auditing and split construction |
| scripts/train.py, train_advanced.py, train_anomaly.py | Reproducible experiments |
| scripts/monitor.py | PCAP or passive interface to JSONL predictions |
| artifacts/, artifacts/extended/, artifacts/advanced/ | Existing trained models; preserve reference copies |
| data/processed/, data/extended/, data/temporal/ | Delivered sample/split data and provenance |
| results/extended/, results/advanced/ | Measured results; not invented example numbers |
| docs/PROJECT_PRESENTATION_FINAL.pptx | Earlier editable presentation retained as a project reference |
| docs/FlowGuard_Detailed_Project_Presentation_v2.pptx | Updated 19-slide detailed presentation with speaker notes |
| docs/FlowGuard_Three_Person_Presentation_Manual.docx and .md | Slide-by-slide rolewise narration, demo plan, handoffs and Q&A for three presenters |
| docs/PROJECT_REPORT.pdf | Existing 16-page technical report |
| docs/WORK_COMPLETED_AND_TEAM_HANDOFF.pdf | Work summary and transfer instructions |
| results/VERIFICATION.txt | Recorded run of 22 passing tests |

## Recorded findings and limits

- Seven-class feature Transformer: accuracy **97.02%**, macro-F1 **0.9409**, benign FPR **4.44%**. Random Forest scored higher: accuracy **99.23%**, macro-F1 **0.9588**.
- Temporal model: **93.88%** accuracy on **196** held-out window endpoints. The temporal test has no infiltration endpoint and only six benign endpoints. These are different evaluation rows from the feature benchmark.
- Infiltration has only five feature-benchmark test examples. Do not present that as strong validation.
- Context timestamps use a documented daytime AM/PM correction heuristic. Windows are nonoverlapping and split-contained, but sampled traffic omits intervening flows and hosts/campaigns may occur across blocks.
- Physical live capture remains unverified on the original computer because Npcap is absent. The custom extractor is not proven CICFlowMeter-equivalent. PCAP replay is tested, with synthetic traffic carrying no attack ground truth.
- FedAvg is local simulation, not a deployed private federation. Online learning requires observed true labels. LIME example fidelity is poor. Anomaly known-attack recall is weak; zero-day detection is not established.
- No production-readiness, architecture novelty, universal accuracy improvement or multi-dataset validation claim is supported.

## Verification and useful commands

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/predict.py --artifacts artifacts/extended --input data/extended/samples/demo_flows.csv --output results/teammate_predictions.csv
.\.venv\Scripts\python.exe scripts/predict_advanced.py --model TemporalTransformer --input data/temporal/test_flows.csv --output results/teammate_temporal.csv
.\.venv\Scripts\python.exe scripts/monitor.py --pcap data/samples/synthetic_pipeline_demo.pcap --output results/teammate_replay.jsonl
```

The project records 22 passing tests from the prior development run. Rerun them on the teammate's environment; library and hardware differences can affect behavior. No raw-source datasets, virtual environment or live capture driver are bundled. Download scripts and pinned provenance are supplied.

## Recommended next work

First reproduce the supplied demo and tests. Then validate extraction parity and physical capture on a configured machine, obtain more rare-class/time-sequence examples, test host/campaign/external-data generalization, and use separate runs for broader tuning. Personalize the report/PPT with team names, registration numbers, institution and guide before submission. Public hosting is a separate optional deployment task.


