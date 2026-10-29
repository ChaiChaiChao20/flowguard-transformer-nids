# Current mapping to the supplied brief

| Brief item | Delivered implementation | Evidence / boundary |
|---|---|---|
| Transformer multi-class NIDS | Trained five/seven-class feature encoders | artifacts/, artifacts/extended/; dashboard |
| DoS, DDoS, Botnet, Port Scan | Four core attacks plus Benign | Core and extended test reports |
| Brute force / infiltration | FTP/SSH brute force and infiltration labels | Extended checkpoint; only five infiltration feature-test examples |
| Flow statistics | 24 statistics with train-only preprocessing | Feature dictionary and split integrity tests |
| IPs, ports, protocol and state | Context inputs, IP buckets/private indicators, categorical protocol/state | 32-feature context schema; flag-derived state, not full TCP reconstruction |
| Long-range traffic relationships | Causal eight-flow Temporal Transformer | Disjoint chronological windows; no proof of arbitrary long-range dependencies |
| CNN/LSTM/GRU/traditional comparisons | Seven models on same feature benchmark | results/extended/model_comparison.csv |
| TabTransformer | Categorical contextual encoder with numeric features | Trained and tested; Extended lab |
| BERT-style encoder | Bidirectional CLS feature encoder trained from scratch | No pretrained NLP BERT or language pretraining claim |
| ViT (optional) | Numerical flow-grid patch Transformer | Trained and tested; not packet imagery |
| SHAP/LIME (optional) | Actual KernelExplainer and LimeTabularExplainer | CLI/dashboard results; poor saved LIME fidelity disclosed |
| Graph network (optional) | Shared-endpoint flow GCN | Batch graph edge tests and checkpoint parity |
| Federated learning (optional) | Three-client weighted FedAvg | Measured local simulation; no privacy/distributed deployment claim |
| Online learning (optional) | Label-gated prequential updates and Page-Hinkley loss detector | Saved stream trace; real-world drift unverified |
| Real-time deployment | Passive interface capture, bounded aggregation, batch alerts | PCAP replay tested; live interface unverified without Npcap |
| Scalability / latency | Chunked source audit, bounded capture, model timings and small replay timing | No production load/capacity certification |
| Accuracy / false-positive improvements | Actual metric comparisons | Random Forest beats feature Transformer; superiority is not assumed |
| Zero-day motivation | Benign-trained atypicality score | Weak known-attack recall; no zero-day validation |
| Dataset choices | CIC-IDS2017 selected from the list | Other datasets are alternatives and were not all trained/evaluated |
| Mininet / NS-3 / SDN custom acquisition | Alternative route described | No included simulator implementation |
| Report, slides, viva and reproducibility | Current PDF/PPTX, guide, source, splits, checkpoints, tests | docs/ and results/VERIFICATION.txt |
| Novelty / research gap | Context and literature discussion | Existing methods acknowledged; publication-level novelty not established |

The remaining deployment work is installing/configuring a capture driver, testing the physical interface, verifying extraction equivalence and validating on target-network traffic. These environment and empirical checks are not represented as completed software features.
