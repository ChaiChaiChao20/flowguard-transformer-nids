# FlowGuard: three-person presentation guide

**Suggested delivery:** about 9 minutes, followed by questions.

Add the three presenters' names and any institution-specific details to the presentation before submission. This guide maps to the supplied 15-slide deck.

## Role split and pacing

| Presenter | Slides | Main responsibility | Suggested time |
|---|---:|---|---:|
| Speaker 1 - Problem, data and model | 1-5 | Introduce FlowGuard, define its scope, explain flow inputs, and describe the Transformer representations. | About 2 min 45 sec |
| Speaker 2 - Training and results | 6-10 | Explain the comparison setup, the measured winner, temporal evaluation, contextual models, and learning simulations. | About 3 min 15 sec |
| Speaker 3 - Demo, limitations and conclusion | 11-15 | Explain interpretability and capture, lead the dashboard demo, summarize limitations, and close. | About 3 min |

Use the scripts as speaking notes, not text to read word-for-word. Keep the two handoffs short and leave questions for after slide 15.

## Speaker 1 - Problem, data and model (Slides 1-5, About 2 min 45 sec)

Introduce FlowGuard, define its scope, explain flow inputs, and describe the Transformer representations.

### Slide 1: FlowGuard

Good morning. Our project is FlowGuard, a network intrusion detection research prototype. It classifies network flows into benign traffic or one of six attack categories. We will show what we built, what the experiments measured, and where the evidence stops.

**Cue:** State your names and course details only after confirming them.

### Slide 2: Scope of the completed implementation

The project includes a seven-class flow classifier, traditional and neural comparison models, contextual and chronological experiments, explanation tools, learning simulations, and a local dashboard. The packet pipeline can replay a capture. Live interface capture is implemented as a path, but it was not validated on the development computer.

**Cue:** Call this a research prototype and local demo.

### Slide 3: Network inputs

The core classifier uses 24 flow statistics such as duration, packet sizes, rates, timing and TCP flags. Context experiments add ports, protocol, state proxies and hashed endpoint indicators. Raw IP addresses help group flows and build graphs; they are not fed to the core classifier as raw numeric values.

**Cue:** Explain a flow as a group of packets between endpoints, summarized for classification.

### Slide 4: Data and evaluation

The benchmark uses sampled CIC-IDS2017 flow data. The seven-class feature test contains only five infiltration examples. The context sample has 15,574 flows, and temporal windows use a documented timestamp correction because the mirror omits AM/PM. These constraints limit how broadly we can generalize the results.

**Cue:** Do not say the project trained on every dataset listed in the original brief.

### Slide 5: Attention architecture

The feature Transformer turns each flow statistic into a token and learns relationships among the feature tokens. A separate Temporal Transformer reads ordered eight-flow windows with a causal mask. Other experiments use categorical attention, numerical patches, or a scratch-trained BERT-style encoder; BERT-style here does not mean pretrained language BERT.

**Cue:** Transition: We have defined the inputs and model choices. Speaker 2 will explain training and measured results.

## Speaker 2 - Training and results (Slides 6-10, About 3 min 15 sec)

Explain the comparison setup, the measured winner, temporal evaluation, contextual models, and learning simulations.

### Slide 6: Training and comparison

We compared Logistic Regression, Random Forest, MLP, CNN, LSTM, GRU and the feature Transformer on the same sampled split. Imputation and scaling were fitted on training data only, while validation selected checkpoints. The reported run used one fixed configuration and seed per model, so it is not an exhaustive model search.

**Cue:** The comparison is controlled for the rows and features used, but not a broad tuning study.

### Slide 7: Seven-class benchmark

The Transformer reached 97.02 percent accuracy and 0.9409 macro-F1. Random Forest scored higher on this run: 99.23 percent accuracy and 0.9588 macro-F1. We report the observed baseline result rather than claiming that attention always improves flow classification.

**Cue:** Say the metric names and support; avoid presenting one score as a deployment guarantee.

### Slide 8: Chronological Temporal Transformer

The temporal model predicts the final flow in each complete, non-overlapping eight-flow window. It scored 93.88 percent accuracy and 0.8003 seven-label macro-F1 on 196 test endpoints. There were no infiltration endpoints and only six benign endpoints, so those classes have weak or absent temporal evidence.

**Cue:** These are sequence endpoints, not the individual-flow test rows from slide 7.

### Slide 9: Graph and alternative models

The graph model links flows that share an endpoint within a batch. TabTransformer adds protocol and state categories, and FlowViT divides numerical features into patches. These are alternative representations for comparison. Their metrics use the saved experiment protocol and do not establish that each extension is better.

**Cue:** Briefly explain one representation; do not read every model name as a list.

### Slide 10: Federated and online extensions

FedAvg was simulated with three clients running locally, with updates combined by sample count. Online learning predicted chronological chunks before true labels were revealed, then used those labels for an update. Neither experiment provides a deployed federation, privacy guarantee, or automatic learning from unverified alerts.

**Cue:** Transition: The measured results have clear boundaries. Speaker 3 will cover explanations, the demo and those limits.

## Speaker 3 - Demo, limitations and conclusion (Slides 11-15, About 3 min)

Explain interpretability and capture, lead the dashboard demo, summarize limitations, and close.

### Slide 11: Explainable predictions

The dashboard includes SHAP and LIME explanations alongside a simpler feature-sensitivity view. The saved LIME example has a surrogate R-squared of 0.144, which is weak fidelity. These methods describe how the model responds to inputs; they do not establish attack causes or prove an explanation is correct.

**Cue:** Mention the low LIME fidelity before interpreting any feature weights.

### Slide 12: Passive capture and replay

The monitor aggregates IPv4 TCP and UDP packets into bounded bidirectional flows, predicts completed flows, and writes JSONL events. A synthetic replay produced 12 flow events from 48 packets. This checks pipeline plumbing, not attack accuracy. Physical capture requires Npcap, and the custom feature extraction has not been shown equivalent to CICFlowMeter.

**Cue:** Never call the synthetic replay an attack-detection evaluation.

### Slide 13: Open and demonstrate

If the local environment is ready, we will classify the included held-out examples in the Extended seven-class profile, then show the performance view. If time allows, we will open the Extended lab or replay the included synthetic capture. If setup fails, we will use the supplied dashboard screenshots and continue without claiming a live capture test.

**Cue:** Presenter 3 controls the screen; Presenter 2 can answer metric questions.

### Slide 14: Measured findings and boundaries

The key measured finding is that Random Forest outperformed the feature Transformer in this benchmark. Rare infiltration support, historical sampled data, one seed, uncertain timestamp correction and possible topology effects limit generalization. Live capture and target-network reliability still need validation. The anomaly score also does not establish zero-day detection.

**Cue:** Frame these as evidence boundaries and concrete next steps.

### Slide 15: References and contribution

Our contribution is a reproducible integration of established models, saved artifacts, measured comparisons and a local demonstration. We acknowledge the source data and methods, and we do not claim a new architecture, production readiness, or zero-day reliability. Thank you. We are ready for your questions.

**Cue:** Close as a team; invite questions and direct them to the relevant speaker.

## Live demonstration plan

1. Before presenting, install the project dependencies once with `powershell -NoProfile -ExecutionPolicy Bypass -File .\SETUP_PROJECT.ps1`.
2. Launch `OPEN_PROJECT.cmd` and use the local URL shown in the terminal.
3. Select **Extended seven classes**, classify the included held-out samples, and show the performance view and per-class support.
4. If time permits, open the **Extended lab** and show one contextual or temporal model. Explain what its input represents before showing its output.
5. Optional PCAP replay command: `.\.venv\Scripts\python.exe scripts\monitor.py --pcap data\samples\synthetic_pipeline_demo.pcap`. Describe it only as a software pipeline demonstration.
6. If the environment is unavailable, use `docs/screenshots/dashboard_predictions.jpg` and `docs/screenshots/extended_lab.jpg`. Do not claim physical live capture was tested.

## Likely questions and who should answer

| Question | Suggested answer | Lead |
|---|---|---|
| Which model performed best? | Random Forest had the highest observed seven-class feature macro-F1 (0.9588); the Transformer scored 0.9409. This is one sampled, fixed-configuration run. | Speaker 2 |
| Why use macro-F1? | It gives each class equal weight, which helps expose performance on less common labels. Always show class support too. | Speaker 2 |
| Why is the temporal score not directly comparable? | It predicts endpoints of eight-flow windows and has 196 test endpoints; the feature benchmark scores individual flows on different rows. | Speaker 2 |
| How did you reduce leakage? | Duplicate feature vectors and conflicting labels were handled before splitting; preprocessing was fit on training rows, validation selected checkpoints, and temporal windows stay within partitions. Hosts or campaigns may still cross blocks. | Speaker 2 |
| Is BERT pretrained? | No. BERT-style describes a bidirectional feature-token encoder trained from scratch, without pretrained language weights. | Speaker 1 |
| Does the system detect zero-day attacks? | That is not established. The classifier predicts known labels, and the anomaly score had weak measured recall on known attacks. | Speaker 3 |
| Was live capture validated? | No. The interface path is implemented, but physical capture was unverified without Npcap. Synthetic PCAP replay only checked software flow. | Speaker 3 |
| Are SHAP and LIME causal explanations? | No. They approximate local model behavior; correlated inputs and low LIME fidelity limit interpretation. | Speaker 3 |

## Final preparation checklist

- Replace role labels with presenter names in your run sheet and add confirmed team, registration, institution and guide details to the deck/report.
- Complete dependency setup before presentation day and confirm the dashboard opens.
- Rehearse speaker handoffs and keep each role within its time.
- Keep slide 7 and slide 8 metrics separate; they refer to different evaluation rows.
- Use the documented wording for simulated, synthetic and unverified features.
- Keep screenshots ready as a fallback for the local demo.
