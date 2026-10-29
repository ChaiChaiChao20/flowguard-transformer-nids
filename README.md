# FlowGuard Network Intrusion Detection

FlowGuard is a runnable research prototype for classifying completed network flows as Benign, DoS, DDoS, Botnet, Port Scan, Brute Force, or Infiltration. It includes a trained feature Transformer, traditional and neural baselines, contextual and temporal experiments, saved results, a Streamlit dashboard, and a passive packet replay pipeline.

The repository is public so you can clone the source and run the dashboard on your own computer. It is not a hosted service: each person runs the app locally at http://127.0.0.1:8502.

## Quick start on Windows

Install Python 3.12 and Git, then run these commands in PowerShell:

    git clone https://github.com/ChaiChaiChao20/flowguard-transformer-nids.git
    cd flowguard-transformer-nids
    py -3.12 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements-extensions.txt
    .\.venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1 --server.port=8502

Open http://127.0.0.1:8502 in your browser. After setup, Windows users can also double-click OPEN_PROJECT.cmd.

## Quick start on macOS or Linux

Install Python 3.12 and Git, then run:

    git clone https://github.com/ChaiChaiChao20/flowguard-transformer-nids.git
    cd flowguard-transformer-nids
    python3.12 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements-extensions.txt
    python -m streamlit run app.py --server.address=127.0.0.1 --server.port=8502

Open http://127.0.0.1:8502. The dashboard and included examples run locally. Physical packet capture depends on the operating system, capture drivers, and permissions; it is not needed for the saved-example demo.

## Try the dashboard

1. Choose **Extended seven classes**.
2. Use an included held-out example and select **Classify flows**.
3. Open **Model performance** to inspect metrics and class support.
4. Use **Extended lab** for saved temporal and alternative-model experiments.

The included checkpoints are ready to use; training and raw-data downloads are not required for the demo.

## Project contents

- app.py — Streamlit dashboard.
- nids/ — schemas, preprocessing, models, inference, context, explainability, and packet aggregation.
- artifacts/ — saved trained models and preprocessing state.
- data/ — sampled feature, contextual, temporal, and demonstration data. Raw source downloads are excluded.
- results/ — measured metrics, predictions, plots, and verification records.
- scripts/ — training, prediction, data preparation, and packet-monitor utilities.
- docs/ — project report, architecture, detailed presentation, three-person guide, and methodology brief.

## Main benchmark result

On the delivered seven-class feature test split, Random Forest achieved macro-F1 **0.9588** and accuracy **99.23%**. The feature Transformer achieved macro-F1 **0.9409** and accuracy **97.02%**. The project reports the measured baseline winner; it does not assume that the Transformer is best.

The split contains only five Infiltration test examples. Temporal results use different prediction units and include no Infiltration endpoint. See the report and requirement traceability document before drawing broader conclusions.

## Reproduce training

The sampled train/validation/test files and preprocessing artifacts are included, so training can be reproduced without downloading full source CSVs:

    python scripts/train.py --epochs 18 --patience 5 --seed 42
    python -m unittest discover -s tests -v

The feature benchmark uses one fixed configuration and seed per model. Results can vary across hardware and library versions.

## Data and evaluation boundaries

CIC-IDS2017 is the selected dataset. The project records pinned mirror provenance, but the mirrors were not independently byte-verified against the original UNB files. The stratified feature split may retain related hosts or campaigns across partitions. The custom packet extractor has not been established as CICFlowMeter-equivalent. PCAP replay is included; physical interface capture was not verified on the prepared computer.

This is a research and teaching prototype. It does not establish production readiness, attack blocking, universal generalization, architecture novelty, or reliable zero-day detection. Read docs/PROJECT_REPORT.pdf, docs/REQUIREMENT_TRACEABILITY.md, and docs/COMPLETE_PROJECT_GUIDE.md for methods, limits, and commands.

## Presentation materials

- docs/FlowGuard_Detailed_Project_Presentation_v2.pptx
- docs/FlowGuard_Three_Person_Presentation_Manual.docx and docs/FlowGuard_Three_Person_Presentation_Manual.md
- docs/PROBLEM_STATEMENT_AND_METHODOLOGY.docx

The names and institution fields in the presentation/manual are left blank for the team to personalize.

