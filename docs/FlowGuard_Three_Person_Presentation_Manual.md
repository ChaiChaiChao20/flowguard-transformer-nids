# FlowGuard — Three-Person Presentation Manual

**Detailed speaker guide for the 19-slide project presentation**

**Presenters:** ____________________  ·  ____________________  ·  ____________________

**Local demo:** http://127.0.0.1:8502

---

## Presentation plan

Aim for **10–12 minutes**, followed by questions. The timings below include speaker transitions; keep the live dashboard demonstration to about one minute.

| Presenter | Slides | Section | Target time |
|---|---:|---|---:|
| Person 1: ____________________ | 1–6 | Problem, scope, data and inputs | 2:45–3:15 |
| Person 2: ____________________ | 7–12 | Model design and measured evaluation | 3:15–3:45 |
| Person 3: ____________________ | 13–19 | Extensions, demo, limits and close | 4:00–4:45 |
| All | Q&A | Assigned answers | As needed |

 > **Core message:** A runnable multi-model research prototype; the evidence does not establish production readiness, zero-day reliability, or Transformer superiority.

### Handoff lines

- **Person 1 → Person 2:** “Now that we have defined the input and the data boundaries, [Name] will explain the model designs and what the benchmark actually measured.”
- **Person 2 → Person 3:** “The core and temporal results have different evidence limits. [Name] will cover the context experiments, the local dashboard and what still needs validation.”
- **Person 3 → Q&A:** “That is our project and the evidence we have so far. Thank you. We are happy to take questions.”

## 2. Setup and live demo

### Start the project

1. On the prepared computer, start the app with OPEN_PROJECT.cmd or run PowerShell with -NoProfile -ExecutionPolicy Bypass and .\launch.ps1 from the project folder.
2. If this is a fresh extraction without .venv, run SETUP_PROJECT.ps1 once, then launch.
3. Open [http://127.0.0.1:8502](http://127.0.0.1:8502). This loopback URL is reachable from the computer running Streamlit; it is not a public website.
4. Keep the terminal and dashboard open throughout the talk. Confirm the dashboard has loaded before the audience arrives.

### One-minute demo script

1. Show the profile selector and choose **Extended seven classes**.
2. Use an included held-out example; select **Classify flows**. Say that this demonstrates inference on supplied rows, not live network traffic.
3. Open **Model performance** and show a metric plus per-class support. Point back to the Random Forest comparison and the five-row Infiltration support.
4. If time allows, open **Extended lab** and show one saved advanced-model result. Do not launch a long training run during the presentation.
5. Return to the prepared slide or stop. If the app is unavailable, use slide 17’s screenshot and say the live demo could not be reached.

**Avoid during the demo:** claiming a public URL, showing real customer traffic, treating probabilities as calibrated certainty, claiming physical interface capture, or suggesting that the app blocks packets.

### Presenter and laptop checklist

- Replace the blank presenter names and add confirmed course/institution details.
- Test slides 10, 12 and 17; open the dashboard before the session.
- Keep a local deck copy. Speaker 3 narrates; assign a teammate to advance slides.
- Avoid starting training, downloads or physical capture during the timed presentation.

## 3. Speaking notes by slide

### Speaker 1 — Project foundations

**Assignment:** Slides 1–6 · **Target:** About 3 minutes · **Presenter:** ____________________

#### Slide 1 — FlowGuard (20 sec)

**Key point:** Introduce FlowGuard as a completed-flow research classifier. Set the expectation that this is a prototype, not an automated blocker.

**Suggested narration:**

Good morning. We are presenting FlowGuard, a network intrusion detection research prototype. It classifies completed network flows as benign or one of six attack categories. We will explain the data, models, measured results, and limits of the evidence.

**Delivery cue:** Add the three presenters' names and confirmed course details before presenting.

**Bridge:** Next, we will define the classification goal and what the package actually contains.

#### Slide 2 — Problem and project goal (30 sec)

**Key point:** Explain why flow summaries are useful and make clear what the model predicts and what it does not do.

**Suggested narration:**

The project studies supervised classification of network-flow records. A flow is a summary of traffic between endpoints, so the model works on features extracted from packets rather than raw payload. The intended result is a class prediction to support analysis, not an intrusion prevention action.

**Delivery cue:** Define a flow in one sentence before listing classes.

**Bridge:** With that goal in view, we can separate completed components from scope boundaries.

#### Slide 3 — What the project includes (35 sec)

**Key point:** Separate implemented functionality from the research scope. Emphasize CIC-IDS2017 as the evaluated source and live capture as unverified.

**Suggested narration:**

The delivered project is broad, but we should describe the boundaries as clearly as the features. CIC-IDS2017 was the chosen dataset. Several other datasets were alternatives in the original brief, not training sources. The dashboard is local. Packet replay is included, while physical interface capture still needs validation.

**Delivery cue:** Do not treat every optional idea in the original checklist as a completed requirement.

**Bridge:** The class counts show why the evaluation needs careful interpretation.

#### Slide 4 — Dataset and seven-class test support (35 sec)

**Key point:** Read the class-support table as part of the result. Call attention to only five Infiltration test flows.

**Suggested narration:**

The seven-class extended feature test contains 1,811 sampled flows. Support is not balanced across classes, and Infiltration has only five examples. That count matters when interpreting its recall or F1. These results describe this fixed sample and do not prove performance on a live network.

**Delivery cue:** Pause on Infiltration = 5; class support is central to interpreting the metrics.

**Bridge:** Those class counts come from a pipeline designed to reserve a held-out test set.

#### Slide 5 — Data preparation and split controls (35 sec)

**Key point:** Describe the held-out test split and training-only preprocessing. Mention the random-split limitation for hosts and campaigns.

**Suggested narration:**

The dataset pipeline audits files, maps labels, removes exact selected-feature duplicates and resolves conflicting labels before creating the feature benchmark. Preprocessing is trained only on the training partition, and validation data selects the checkpoint. The report also documents the limits of random splits: related hosts or campaigns may still occur across partitions.

**Delivery cue:** Say how leakage controls help, then state what they cannot guarantee.

**Bridge:** After data preparation, the next question is what information reaches the models.

#### Slide 6 — What goes into a model? (30 sec)

**Key point:** Contrast the core 24-feature model inputs with the richer context inputs; explain that endpoint data can encode dataset topology.

**Suggested narration:**

The core model receives 24 flow statistics. Context experiments add ports, protocol, endpoint-derived features and a state proxy. Raw IP addresses are used to group temporal activity and construct graph edges. Context models use deterministic hash buckets and private-status features, so collisions and dataset-specific topology remain possible.

**Delivery cue:** Distinguish the core 24-feature input from the larger context input.

**Bridge:** Speaker 2 will now explain the architectures and the benchmark results.

---

### Speaker 2 — Models and evaluation

**Assignment:** Slides 7–12 · **Target:** About 3½ minutes · **Presenter:** ____________________

#### Slide 7 — Two Transformer tasks (30 sec)

**Key point:** Use the side-by-side diagram to distinguish attention over features in one flow from attention over a sequence of flows.

**Suggested narration:**

There are two distinct attention tasks. The core feature Transformer attends among feature tokens inside one flow. The temporal model attends across a chronological window of eight flow records and predicts the last flow. The CNN, LSTM and GRU baselines scan fixed feature order; they are not temporal traffic models.

**Delivery cue:** Use this distinction throughout the presentation; do not call every sequence model temporal.

**Bridge:** The feature Transformer gives us a concrete example of attention over one flow.

#### Slide 8 — Feature Transformer architecture (30 sec)

**Key point:** Walk from 24 measurements to feature/value tokens, the CLS summary, and seven class scores. Avoid implying a large language model.

**Suggested narration:**

The feature Transformer tokenizes the 24 input values and adds learned feature identities. A CLS token summarizes the tokens. The encoder has two layers, four attention heads and dimension 32, followed by a seven-class head. It is a feature-relation model for individual flows, not a model of long traffic history.

**Delivery cue:** Walk left to right and name what each representation means.

**Bridge:** Next we will explain how the model comparison was controlled.

#### Slide 9 — Comparison and training protocol (35 sec)

**Key point:** Explain fair comparison controls and their boundary: shared split/features, validation checkpoint selection, one seed/configuration.

**Suggested narration:**

The seven-model comparison uses matching rows and features. Neural models use AdamW, a learning rate of 0.001, weighted cross-entropy, batch size 256 and gradient clipping, with validation macro-F1 for checkpoint choice. Each model uses one fixed configuration and seed. The evidence is controlled for the delivered split, but not an exhaustive tuning study.

**Delivery cue:** Mention the one-seed limitation before drawing broad model conclusions.

**Bridge:** Here are the measured outcomes from that controlled split.

#### Slide 10 — Seven-class benchmark results (50 sec)

**Key point:** State the measured winner first, then compare the Transformer. Discuss both macro-F1 and benign false-positive rate.

**Suggested narration:**

On this fixed split, Random Forest achieved the highest macro-F1 at 0.9588. The feature Transformer scored 0.9409, and CNN scored 0.9539. Random Forest accuracy was 99.23 percent and benign false-positive rate was 0.89 percent; the Transformer reached 97.02 percent accuracy and a 4.44 percent benign false-positive rate. We report the measured baseline winner rather than assuming attention wins.

**Delivery cue:** Point to the Random Forest bar, then state why this does not prove universal superiority.

**Bridge:** The headline score is only part of the result; rare-class support changes confidence.

#### Slide 11 — Rare-class support changes the conclusion (35 sec)

**Key point:** Pause on the denominator of five. Explain why 3/5 recall is not stable evidence for rare-attack detection.

**Suggested narration:**

The Transformer classified three of the five Infiltration test flows correctly, giving 0.60 recall and 0.75 F1 in this split. With only five test examples, a single example changes recall by 20 percentage points. This is an evaluation warning, not evidence that Infiltration detection is dependable.

**Delivery cue:** Do not hide this result behind overall accuracy.

**Bridge:** The temporal experiment uses different prediction units, which we will now examine.

#### Slide 12 — Temporal results are a different task (35 sec)

**Key point:** Read 93.88% and 0.8003 together with 196 endpoints and the missing Infiltration endpoint; do not compare directly with slide 10.

**Suggested narration:**

The temporal model predicts the endpoint of complete eight-flow windows. It scored 93.88 percent accuracy and 0.8003 macro-F1 across seven labels on 196 endpoints. The test split contains no Infiltration endpoint and only six Benign endpoints. Those outputs are not directly comparable with the individual-flow benchmark because the evaluation units differ.

**Delivery cue:** Point out the missing Infiltration support on the confusion matrix.

**Bridge:** Speaker 3 will cover the additional models and the local dashboard demonstration.

---

### Speaker 3 — Extensions and project demo

**Assignment:** Slides 13–19 · **Target:** About 4½ minutes, including a short demo · **Presenter:** ____________________

#### Slide 13 — Context models add network signals (35 sec)

**Key point:** Name the context models and their common 3,526 output rows. Say these are experiments with different inductive biases and documented limitations.

**Suggested narration:**

The context models use additional network information in different ways. BERTStyleEncoder is a bidirectional feature encoder trained from scratch; TabTransformer embeds categorical inputs; FlowViT uses numerical patches; and the graph network connects flows sharing an endpoint inside a batch. Each produced 3,526 individual-flow test outputs. These experimental rows should be interpreted with the documented protocol and topology limits.

**Delivery cue:** Explain one model representation; emphasize that BERT-style is not pretrained BERT.

**Bridge:** The project also explores whether learning can adapt across clients or over time.

#### Slide 14 — Adaptation studies are simulations (35 sec)

**Key point:** Distinguish a local FedAvg simulation from deployed federation, and supervised online updates from unlabeled learning.

**Suggested narration:**

The FedAvg experiment simulates three local clients and sample-weighted model aggregation over three rounds; it does not provide a privacy guarantee. The online experiment predicts before revealing true labels and updates with those labels. It is a supervised adaptation study, not unlabeled online learning.

**Delivery cue:** Use the word simulation; do not claim privacy or real-world drift validation.

**Bridge:** Now we will look at what the explanation and anomaly tools can and cannot tell us.

#### Slide 15 — Explainability and anomaly flags (40 sec)

**Key point:** Explain one SHAP case, weak LIME fit, and low known-attack anomaly recall; keep the interpretation local and limited.

**Suggested narration:**

The saved SHAP example reports its reference probability, attribution sum and reconstructed DDoS probability. The LIME example has R-squared 0.1440, which is weak fidelity and limits interpretation. The anomaly flag is based on a benign-trained Isolation Forest, but its known-attack recall is only 1.98 percent. Neither method establishes causal explanations or zero-day reliability.

**Delivery cue:** Lead with the LIME limitation and the weak anomaly recall.

**Bridge:** The same caution applies to packet replay and capture: pipeline operation is not attack validation.

#### Slide 16 — Packet replay and capture path (35 sec)

**Key point:** Describe packet-to-flow-to-prediction plumbing, then state that the 48-packet replay is not an accuracy or production-throughput test.

**Suggested narration:**

The monitor groups IPv4 TCP and UDP packets into bounded bidirectional flows, predicts completed flows and writes JSONL records. The synthetic replay processed 48 packets into 12 events in 0.207 seconds, about 58 flows per second. This tiny plumbing run is not a production benchmark or attack-accuracy evaluation. Live capture requires Npcap and target-interface validation.

**Delivery cue:** Describe this as packet-to-event plumbing, not real-time attack detection.

**Bridge:** We will show the app locally, then close with what must be validated next.

#### Slide 17 — Local dashboard demonstration (70 sec)

**Key point:** Demonstrate the dashboard using a saved sample; show class support/performance; end in Extended lab if time permits.

**Suggested narration:**

The dashboard provides profile selection, sample classification, metrics, model comparisons and an Extended lab. We can show the current local app at http://127.0.0.1:8502. Start with included samples, open performance and class support, then show one advanced model if time permits. If the app is unavailable, use the supplied screenshot and do not claim that physical capture was demonstrated.

**Delivery cue:** Presenter 3 controls the screen. Presenter 2 handles metric questions.

**Bridge:** These are the practical next steps before any operational use.

#### Slide 18 — What remains to validate (25 sec)

**Key point:** List concrete validation work that would improve evidence: interface capture, extraction parity, rare-class support, independent splits and seeds.

**Suggested narration:**

The main follow-up work is validation. Physical capture needs an installed driver and interface testing. The packet extractor must be compared with the training feature definitions. The experiments need more rare-class sequences, stronger host or campaign holdouts, more seeds and external datasets. Target-network false-alert rates and load also need evaluation before considering deployment.

**Delivery cue:** Present these as the next research steps; do not imply they have already been done.

**Bridge:** To conclude, we will summarize the central result and take your questions.

#### Slide 19 — Conclusion and selected references (30 sec)

**Key point:** Close on what the evidence supports and what it does not. Thank the audience and invite questions.

**Suggested narration:**

To conclude, this project provides a reproducible implementation and an honest evaluation of established methods. In this benchmark, Random Forest outperformed the feature Transformer. The project does not establish architecture novelty, production readiness or zero-day reliability. Thank you; we are ready for questions. Full references are in the report.

**Delivery cue:** Close together and invite questions. Add confirmed names and institution details before submission.

---

## 4. Likely questions and supported answers

Keep answers short, factual and tied to the supplied experiment. If the package does not contain evidence, state the gap and next validation step.

### Which model performed best?

**Suggested answer (Person 2):** Random Forest had the top macro-F1, 0.9588, on this fixed seven-class feature split. The Transformer scored 0.9409. We report the baseline winner; each model used one configuration and seed, so this is not a broad tuning study.

### Why report macro-F1 instead of accuracy?

**Suggested answer (Person 2):** Macro-F1 gives each class equal weight in the average, so a large class cannot dominate the summary. We still report accuracy, class support, and false-positive rate because every metric answers a different question.

### Can we trust the Infiltration score?

**Suggested answer (Person 2):** Not as a stable estimate. There are only five Infiltration examples in the feature test split; three were correctly classified by the Transformer. One example changes recall by 20 percentage points.

### Why is the temporal accuracy not directly comparable?

**Suggested answer (Person 2):** The temporal task predicts the last flow in an eight-flow window and scores 196 window endpoints. The feature benchmark scores individual flow rows; the temporal support also lacks an Infiltration endpoint and has only six Benign endpoints.

### Is this a production or real-time capture system?

**Suggested answer (Person 3):** The Streamlit dashboard and synthetic PCAP replay run locally. Physical interface capture needs Npcap and interface validation, and feature-extraction parity against the training definition remains unverified. We do not claim production readiness.

### Does it detect zero-day attacks?

**Suggested answer (Person 3):** The classifier is trained on known labels. The benign-trained Isolation Forest has only 1.98% recall on the included known-attack sample. The evidence does not establish zero-day detection.

### Is BERTStyleEncoder pretrained on text?

**Suggested answer (Person 3):** No. In this project it is a BERT-style bidirectional feature encoder trained from scratch on flow features; it is not a pretrained language model.

### Do SHAP and LIME prove why the model made a decision?

**Suggested answer (Person 3):** No. SHAP is a local attribution for one saved example. The LIME example has R-squared 0.1440, which is weak local fit. Neither establishes causality or reliable explanations across all rows.

### Does FedAvg guarantee privacy?

**Suggested answer (Person 3):** No. The delivered experiment simulates three clients inside one process and averages model weights. It does not include secure aggregation, privacy accounting, or networked client transport.

### Which datasets were evaluated?

**Suggested answer (Person 1):** CIC-IDS2017 is the selected dataset for the delivered benchmark. Other datasets in the original project brief were alternatives; they were not all trained and evaluated.

### What is the main next experiment?

**Suggested answer (Person 3):** Validate physical capture and feature parity, then evaluate with more rare-class examples, host/campaign holdouts, repeated seeds, external data, and target-network false-alert measurements.

### Why use a Transformer if Random Forest is higher?

**Suggested answer (Person 2):** The project evaluates the Transformer rather than assuming it wins. The benchmark establishes a useful comparison and the delivered result says Random Forest is stronger on this split; a Transformer can remain a research option if further evidence supports it.


## 5. Technical wording to keep consistent

| Term | Plain-language meaning |
|---|---|
| Flow | A summary of packets between endpoints over a bounded interval; the core classifier predicts one label per completed flow. |
| Accuracy | Fraction of all evaluated examples classified correctly; it can be dominated by common classes. |
| Macro-F1 | F1 computed per class and averaged equally, so rare classes contribute equally to the summary. |
| False-positive rate | Share of benign examples predicted as an attack for the stated evaluation. |
| Temporal endpoint | The final flow being predicted from one chronological eight-flow window. |
| Local dashboard | A Streamlit app bound to loopback at 127.0.0.1:8502 on the prepared computer. |
| FedAvg simulation | A local simulation of model-weight averaging across three clients; no privacy guarantee is included. |
| Zero-day | An attack outside the labels/examples used for development; this project does not establish reliable detection of such attacks. |

## 6. Source materials and rehearsal note

The new deck and manual use the project’s delivered code, metrics, plots, screenshots and documentation. Consult docs/PROJECT_REPORT.pdf for full methods/citations and docs/REQUIREMENT_TRACEABILITY.md for implementation boundaries. The original report and presentation remain project references. Do not invent presenter names, institution details or performance claims.

Rehearse the two handoffs, the slide 10 winner, the five-row Infiltration denominator, the missing temporal support, and the demo fallback.
