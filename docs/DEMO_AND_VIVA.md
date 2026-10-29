# Demonstration and viva

## Six-minute demonstration

1. Double-click OPEN_PROJECT.cmd. Explain that training artifacts are already supplied.
2. Select Extended seven classes and classify the 65 held-out examples. There are up to ten per class and five infiltration examples. Ground truth is separate from input.
3. Open Model performance. Show Transformer and Random Forest results, per-class support and the infiltration limitation.
4. Open Extended lab. Run TemporalTransformer on chronological test flows. Explain eight-flow endpoints, causal masking and the missing infiltration test window.
5. Select TabTransformer, FlowViT or FlowGraphNetwork. Explain each representation rather than claiming they all outperform baselines.
6. Compute SHAP. Explain reference probability plus contributions. Show LIME and its local fidelity value; poor fidelity limits conclusions.
7. Replay the included PCAP using monitor.py. Show JSONL metadata, predictions, attack flags and anomaly scores. Explain Npcap dependency and extraction-domain shift.
8. Show report, presentation, traceability and recorded verification.

## Viva answers

**Why a Computer Networks project?** Flow aggregation uses endpoint five-tuples, transport flags, timing, direction, packet counts/lengths and throughput. Temporal windows and endpoint graphs add traffic context, while the passive pipeline connects packets to predictions.

**What does self-attention do?** The feature encoder learns relationships between numeric feature tokens. The temporal encoder attends across chronological flow tokens with a causal mask. Neither proves every long-range dependency is captured.

**What attacks are classified?** Benign, DoS, DDoS, Botnet, Port Scan, FTP/SSH Brute Force and Infiltration. Unsupported labels are excluded rather than called benign.

**How do DoS and DDoS differ?** Distributed attacks involve multiple sources. Historical per-flow labels do not guarantee reliable operational distinction; context and external validation matter.

**Which model won?** Random Forest had the highest seven-class feature-benchmark macro-F1. The report records the observed result rather than assuming Transformer superiority.

**Why macro-F1 and support?** Equal per-class averaging prevents common classes from dominating. Rare infiltration has only five feature test examples and no temporal test endpoint, which severely limits evidence.

**How is leakage controlled?** Numeric-vector deduplication/conflict removal precedes splits; preprocessing is trained only on training rows; validation selects checkpoints; test does not select configurations. Temporal windows are disjoint and never cross partitions. Hosts/campaigns can still cross blocks.

**Are the timestamps fully verified?** No. The mirror omits AM/PM. A recorded daytime heuristic corrects hours 01..07; it has not been independently validated against original PCAP timing.

**Are the baseline LSTM/GRU temporal?** Those baseline models scan fixed feature order. The separate TemporalTransformer uses real timestamp ordering and complete eight-flow windows.

**How are IP addresses used?** Context models use deterministic buckets and private-status indicators. Raw addresses form host groups and graph edges. Buckets collide and can encode dataset topology, so cross-network generalization is unproven.

**Is BERT pretrained?** No. BERT-style denotes a bidirectional CLS feature encoder trained from scratch, without NLP BERT weights or masked-language pretraining.

**What is the ViT input?** A numerical flow-feature grid divided into four-value patches. It is not a packet-image dataset.

**What does the GCN graph represent?** Flow nodes sharing source or destination endpoints within one consecutive batch have edges. Graph context never crosses a data split, but predictions depend on batch composition.

**Is federated learning deployed?** No. Three local simulated IID clients perform sample-weighted FedAvg over three rounds. No secure aggregation, differential privacy or transport is implemented.

**How does online learning avoid unsafe pseudo-labels?** The experiment predicts before true stream labels are revealed, then updates with those observed labels at a fixed rate. It never assumes its predictions are ground truth. The drift detector monitors observed loss.

**Are SHAP/LIME causal explanations?** No. They explain local model behavior relative to backgrounds/perturbations. Correlated features and poor LIME surrogate fit can make interpretations unreliable.

**Is this real-time?** A passive interface path is implemented and PCAP replay is tested. Physical capture is unverified on this computer without Npcap. Flow completion, buffering, extraction and model latency all matter; production real-time reliability is not established.

**Can it detect zero-day attacks?** The closed-set classifier predicts known labels. A benign-trained anomaly flag is supplied, but known-attack anomaly recall is weak and no unseen-attack evaluation establishes zero-day performance.

**What is the contribution?** A reproducible integration of established methods with trained checkpoints, networking context, packet replay, explanations and honest comparative evidence. A new architecture or publication-level novelty is not claimed.

**What remains for deployment?** Driver configuration, physical-interface validation, extraction equivalence, realistic load and target-network false-alert testing, stronger host/campaign splits, more rare attack sequences and probability calibration.
