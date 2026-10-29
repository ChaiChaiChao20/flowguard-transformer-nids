# Complete project: opening, experiments and deployment

## Open the dashboard

On a new computer, run `powershell -NoProfile -ExecutionPolicy Bypass -File .\SETUP_PROJECT.ps1` once to create `.venv` and install dependencies. Then double-click `OPEN_PROJECT.cmd` in the project folder. Keep its terminal open and visit the URL it prints (normally http://127.0.0.1:8502).

The sidebar offers **Core five classes** and **Extended seven classes**. Choose the extended profile, then **Classify flows**. In **Extended lab**, choose one of the seven advanced models and **Run advanced model**. SHAP and LIME buttons explain the first held-out sample for the selected classifier profile.

## What is included

| Component | Where to use it |
|---|---|
| Five/seven-class feature Transformer + six baselines | Analyze flows; Model performance |
| Temporal Transformer on eight chronological flows | Extended lab; TemporalTransformer |
| TabTransformer with protocol/state categorical attention | Extended lab; TabTransformer |
| ViT on numerical flow-feature patches | Extended lab; FlowViT |
| BERT-style bidirectional CLS encoder, trained from scratch | Extended lab; BERTStyleEncoder |
| GCN with shared-endpoint graph edges | Extended lab; FlowGraphNetwork |
| Three-client FedAvg simulation | Extended lab; FederatedFedAvg |
| Label-gated online learning + loss drift detector | Extended lab; OnlineLearning |
| SHAP KernelExplainer and LIME Tabular | Extended lab explanation buttons or scripts/explain.py |
| Benign-trained anomaly score | Extended-profile predictions, atypical_flag |
| Passive flow capture and JSONL events | scripts/monitor.py |

The listed datasets in the assignment are alternatives. CIC-IDS2017 is used here; models have not been trained on every listed dataset. Mininet/NS-3/SDN custom datasets are another optional acquisition route rather than an included simulator implementation.

## Command-line examples

Run commands in the project folder using the prepared environment's python.exe, or a virtual environment installed from requirements-extensions.txt.

```powershell
python scripts/predict.py --artifacts artifacts/extended --input data/extended/samples/demo_flows.csv --output results/my_seven_class_predictions.csv
python scripts/predict_advanced.py --model TemporalTransformer --input data/temporal/test_flows.csv
python scripts/predict_advanced.py --model FlowGraphNetwork --input data/temporal/test_flows.csv
python scripts/explain.py --method shap
python scripts/explain.py --method lime
python scripts/monitor.py --pcap data/samples/synthetic_pipeline_demo.pcap --output results/my_replay.jsonl
```

For context CSVs provide the 24 statistical columns plus `source_ip`, `destination_ip`, `source_port`, `destination_port`, `protocol` and ISO `Timestamp`. Ports must be 0..65535. Protocol accepts TCP/UDP/ICMP or numeric codes. State is inferred from FIN/RST flags; it is not a full TCP state machine. Temporal input is sorted by time within source/day and reset after a 300-second idle gap; only complete eight-flow windows produce an output. Graph inference creates endpoint edges within consecutive 128-flow batches, without crossing CSV boundaries.

## Physical live capture on Windows

1. Install the packet-capture driver from the official [Npcap website](https://npcap.com/), following its installation and licence instructions.
2. Open a terminal with the capture permissions required by your installation.
3. Run `python scripts/monitor.py --list-interfaces` and copy the exact desired interface identifier.
4. Run `python scripts/monitor.py --interface "YOUR_INTERFACE" --seconds 60`.
5. Inspect `results/live_events.jsonl` and its summary JSON. Every event contains flow metadata, statistics, seven-class probabilities, attack flag and anomaly score.

The program observes traffic and does not generate attacks or block connections. It aggregates IPv4 TCP/UDP only, with idle/active timeouts, packet-count caps and bounded active-flow storage. The local extractor uses IP packet lengths, population standard deviations and per-packet TCP flag counts. It differs from CICFlowMeter, so inference is experimental until extraction equivalence and target-network performance are tested. Closing on FIN/RST and timeout decisions also affect flow semantics. Completed-flow timeout contributes to alert latency.

Npcap is absent on the development computer. PCAP replay, aggregation arithmetic and prediction were tested. Physical-interface capture and deployment attack accuracy are not validated. The synthetic demonstration PCAP tests software plumbing and has no attack ground truth.

## Interpretation of the optional research modules

**Federated learning:** three clients execute local training and sample-weighted aggregation in one Python process. No secure aggregation, differential privacy, distributed transport or privacy guarantee is provided.

**Online learning:** the experiment predicts validation-stream chunks before revealing their true labels, then updates at a fixed learning rate. It saves prequential scores and evaluates a frozen adapted model on the test split. Unlabeled network alerts are never automatically treated as correct training labels. Page-Hinkley detects increases in observed loss; drift detection is unit-tested but no real-world drift claim is made.

**Explainability:** SHAP includes its reference probability and additive attribution check. LIME includes local-surrogate R-squared; poor fidelity should prevent strong explanation claims. Neither method proves causality.

**Zero-day motivation:** the atypicality flag is an Isolation Forest trained on benign data, with a threshold selected only from validation benign scores. Its measured known-attack recall is low. No unseen-attack or zero-day reliability is established.

**Chronology:** the mirror omits AM/PM. A documented working-day heuristic shifts hours 01..07 to 13..19. Sampled chronology omits intervening flows; hosts/campaigns can still cross split blocks. The rare infiltration class has no complete held-out temporal window in this run, so temporal infiltration performance is unmeasured even though the seven-class feature benchmark tests it.

## Submission

Use PROJECT_REPORT.pdf and FlowGuard_Detailed_Project_Presentation_v2.pptx as the current report/deck. Add your name, registration number, institution and guide. Use REQUIREMENT_TRACEABILITY.md to distinguish implemented methods, measured evidence, alternative datasets and deployment tasks. The project demonstrates working implementations; it does not prove novel architecture, model superiority, production readiness or zero-day detection.

