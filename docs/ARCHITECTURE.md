# FlowGuard architecture

```mermaid
flowchart TD
    A[Recorded flow data] --> B[Audit, deduplication and conflict removal]
    B --> C[Random feature splits / chronological activity blocks]
    C --> D[Training-only imputation, log transform and scaling]
    D --> E[Feature encoder and six baselines]
    D --> F[Contextual tabular and flow-grid encoders]
    D --> G[Disjoint eight-flow causal windows]
    G --> H[Temporal Transformer]
    D --> I[Shared-endpoint flow graph]
    I --> J[GCN]
    F --> K[FedAvg client simulation / labeled online updates]
    E --> L[Saved checkpoints and measured held-out evidence]
    H --> L
    J --> L
    K --> L
```

```mermaid
flowchart LR
    A[PCAP / passive live interface] --> B[Bounded IPv4 TCP/UDP aggregation]
    B --> C[Completed flow statistics]
    C --> D[Saved preprocessing]
    D --> E[Seven-class Transformer + anomaly score]
    E --> F[JSONL prediction events]
    G[CSV or chronological context flows] --> H[Dashboard and CLI]
    H --> I[Feature / temporal / graph / alternative inference]
    H --> J[SHAP and LIME]
```

The packet extractor is custom and has not been validated as CICFlowMeter-equivalent. PCAP replay is tested; physical live capture requires Npcap and suitable capture permissions. Classification does not block traffic. Context state is a flag-derived proxy. Adaptation requires real labels.
