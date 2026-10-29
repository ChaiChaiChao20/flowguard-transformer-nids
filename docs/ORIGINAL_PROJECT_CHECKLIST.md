# Project implementation checklist

**Title:** Transformer-Based Network Intrusion Detection System for Intelligent Multi-Class Cyber Attack Classification

**Purpose:** Build a working student project that takes network-flow features as input and predicts normal traffic or a specific attack category. Compare a Transformer with other models, evaluate it honestly, and demonstrate predictions in a simple interface.

This plan uses the attached project brief as reference. The tool choices, schedule, and starting model settings below are suggested implementation decisions, not additional requirements from your faculty.

## 1. Confirm the project scope

- [ ] Write a one-page problem statement, objectives, scope, and expected output.
- [ ] Confirm with the guide whether classification of individual flows is sufficient or whether a temporal sequence of flows is required.
- [ ] Define the first version: an offline flow-based classifier, comparison experiments, and a CSV-upload demo.
- [ ] Define target classes: **Benign, DoS, DDoS, Botnet, and Port Scan**.
- [ ] Decide whether brute force, web attacks, and infiltration are additional classes or excluded from the first version. Never relabel excluded attacks as benign.
- [ ] Confirm whether the guide requires CNN, LSTM, and GRU comparisons as well as traditional machine-learning baselines; the brief mentions these comparisons.
- [ ] Record the submission date, review dates, team roles, and available laptop/GPU resources.

**Finish this step with:** an agreed scope and a list of required deliverables.

## 2. Understand the networking and machine-learning concepts

- [ ] Study packets versus flows, source/destination ports, TCP/UDP, TCP flags, flow duration, packet counts, packet sizes, and inter-arrival times.
- [ ] Understand how DoS, DDoS, botnet traffic, and port scans differ at the network level.
- [ ] Understand signature-based IDS, anomaly-based IDS, and supervised classification.
- [ ] Learn training/validation/test splits, class imbalance, overfitting, data leakage, precision, recall, and F1 score.
- [ ] Learn feature embeddings, self-attention, multi-head attention, Transformer encoders, pooling, and classification heads.
- [ ] Prepare a short literature comparison table: paper, dataset, representation, model, metrics, limitations, and relevance. Start with 5–8 credible papers; follow your faculty's required count.

**Finish this step with:** background notes and a literature survey. Treat the brief's research-gap and novelty statements as claims to investigate, not established findings.

## 3. Set up the development environment

- [ ] Use Python with pandas/NumPy for data handling, scikit-learn for preprocessing/baselines/metrics, PyTorch for the Transformer, and Matplotlib or Seaborn for plots.
- [ ] Use Jupyter or a code editor for development; use a simple Streamlit interface for the demonstration if suitable.
- [ ] Create a virtual environment and record package versions in a dependency file.
- [ ] Create folders for raw data, processed data, notebooks, source code, model checkpoints, experiment results, demo, and report.
- [ ] Use version control and record a random seed and experiment configuration.
- [ ] Verify that a small neural-network example runs on your hardware. Start small before using the full dataset.

**Finish this step with:** a reproducible environment and project folder structure.

## 4. Select and inspect the dataset

- [ ] Suggested first dataset: **CIC-IDS2017**, using its machine-learning CSV files. It provides labeled network-flow data and includes attacks relevant to the proposed scope.
- [ ] Download from the official source and record the source URL, file names, access date, and required citation.
- [ ] Read the documentation and inspect the actual labels and feature columns in your downloaded version.
- [ ] Create a data dictionary explaining each selected feature and its unit.
- [ ] Count examples per class and plot the class distribution.
- [ ] Check missing values, infinite values, duplicates, inconsistent column names, and suspicious constant columns.
- [ ] Save an explicit label mapping. For example, map the supported DoS subtype labels to DoS and the Bot label to Botnet; verify the exact names in the files.
- [ ] Preserve original labels and document every grouping, exclusion, and sampling decision.
- [ ] If data must be sampled for your hardware, retain enough minority-class examples and record the sampling method.

**Finish this step with:** a dataset summary, feature list, class counts, and label-mapping table.

## 5. Prepare the data without leakage

- [ ] Standardize column names and clean invalid values using a documented rule.
- [ ] Remove duplicates or keep related duplicates in the same split so the same example does not appear in both training and testing.
- [ ] Keep metadata needed for splitting, but exclude labels, flow identifiers, and obvious attack-specific identifiers from model inputs. Consider excluding IP addresses and timestamps to reduce shortcut learning; justify any retained ports or identifiers.
- [ ] Reserve separate training, validation, and test sets. A 70/15/15 split is a starting choice where appropriate, not a requirement.
- [ ] Prefer grouping by session/capture or time where feasible. Verify class coverage: CIC-IDS2017 attacks occur on particular days, so a simple day split can omit classes from training or testing.
- [ ] If using a random stratified split, document its limits and check for related-flow leakage.
- [ ] Fit imputation, scaling, encoding, and any feature selection on **training data only**, then apply the saved transformations to validation and test data.
- [ ] Address imbalance first with training-derived class weights. Apply any resampling only to the training set.
- [ ] Save the preprocessing pipeline, ordered feature names, label mapping, and split manifest.

**Finish this step with:** reproducible model-ready data and an untouched test set.

## 6. Train comparison models

- [ ] Train a simple baseline, such as Logistic Regression or a Decision Tree.
- [ ] Train a stronger traditional baseline, such as Random Forest.
- [ ] Implement CNN, LSTM, and GRU comparisons if required by the approved scope.
- [ ] Explain how each deep model receives the inputs. Feature order is not automatically a time sequence.
- [ ] Use the same dataset split, labels, feature information, and metrics for a fair comparison.
- [ ] Tune models on validation data with a documented and reasonably comparable tuning budget.
- [ ] Save validation results, training time, and model configurations.

**Finish this step with:** baseline checkpoints and a comparison-results template.

## 7. Design and implement the Transformer

**Recommended manageable first version: feature-token Transformer.** Each feature in one flow becomes a token with a learned feature identity and an embedding of its value. The encoder learns relationships among features. This representation does **not** demonstrate long-range temporal dependencies between flows.

- [ ] Decide between feature tokens and a temporal flow sequence, based on the approved scope.
- [ ] For feature tokens, implement a numeric-value embedding plus learned feature-identity embeddings. Handle categorical values with an appropriate categorical embedding if included.
- [ ] For a temporal model, define flow grouping, timestamp order, window length, padding/masks, and the prediction target. Construct windows within splits so overlapping windows cannot leak across sets.
- [ ] Build the architecture: **tokens → Transformer encoder → pooling → dense classifier → class logits**.
- [ ] Choose a small starting configuration, for example embedding size 64, 4 attention heads, 2 encoder layers, and dropout 0.1. Adjust using validation results and hardware limits.
- [ ] Ensure the embedding dimension is divisible by the number of attention heads.
- [ ] Make the classifier output dimension equal to the number of selected classes.
- [ ] Use multi-class cross-entropy on logits; apply softmax when displaying prediction scores.
- [ ] Check input shapes, output shapes, masks if used, and one training batch before a full run.

**Finish this step with:** an architecture diagram and a functioning Transformer model.

## 8. Train and tune the model

- [ ] Choose an optimizer such as AdamW and a starting learning rate such as 0.001; tune it on validation data.
- [ ] Select a batch size your hardware can support.
- [ ] Use class weights if appropriate, early stopping, and checkpoint saving.
- [ ] Track training/validation loss and macro-F1 across epochs.
- [ ] Tune only a small, recorded set of settings: learning rate, model size, dropout, and class-weight strategy.
- [ ] Save the best model according to a predefined validation metric, such as macro-F1.
- [ ] Repeat the final configuration with several seeds if time permits and report variation.
- [ ] Keep the test set out of model selection.

**Finish this step with:** the selected checkpoint, learning curves, and experiment log.

## 9. Evaluate the completed models

- [ ] Evaluate the selected models on the reserved test set after model selection.
- [ ] Report accuracy, macro-F1, weighted-F1, and per-class precision, recall, F1, and sample count.
- [ ] Plot raw-count and normalized confusion matrices.
- [ ] Calculate benign false-positive rate: benign flows predicted as any attack divided by all benign flows.
- [ ] Examine missed attacks and confusion between attack categories, especially rare classes.
- [ ] Compare model performance, training time, inference time, model size, and hardware used.
- [ ] State inference batch size and whether timing includes preprocessing. Classification of completed flows also requires flow collection/extraction time.
- [ ] Run a useful ablation, such as removing attention and using a comparable MLP, to assess whether attention helps.
- [ ] Report results honestly even if a baseline performs better. Do not promise an accuracy percentage before measuring it.
- [ ] Limit conclusions to the evaluated setting. Closed-set classification does not establish zero-day detection, and dataset scores do not establish production readiness.

**Finish this step with:** final tables, plots, error analysis, and a conclusion supported by measurements.

## 10. Build the demonstration

- [ ] Load the saved preprocessing pipeline, feature schema, label mapping, and Transformer checkpoint.
- [ ] Provide a CSV-upload interface and a small example file with the required feature columns.
- [ ] Validate missing columns, column order, invalid values, and incorrect input types.
- [ ] Show predicted class and model probability score for each flow; probability scores are not guaranteed calibrated confidence.
- [ ] Show a chart of predicted class counts and allow prediction results to be downloaded.
- [ ] Demonstrate known held-out examples from normal traffic and each supported attack class.
- [ ] Verify that the demo and evaluation code produce the same predictions for the same inputs.
- [ ] Test loading the saved model in a fresh session without retraining.

**Finish this step with:** a reproducible offline demo. Raw PCAP upload needs a feature-extraction pipeline; a CSV classifier alone cannot process packets directly.

## 11. Add extensions only after the core system works

- [ ] Optional: feature explanations using SHAP or LIME, with the explainer and its limitations documented. Attention weights alone are not proof of an explanation.
- [ ] Optional: replay a saved traffic capture through a compatible flow extractor and measure the complete pipeline.
- [ ] Optional: live capture in an authorized lab, using exactly the feature definitions and units expected by the trained model.
- [ ] Optional: test on a second dataset only after reconciling feature definitions and class mappings.
- [ ] Optional: temporal attention experiments if ordered flow data is available.

Federated learning, graph neural networks, online learning, and flow-image/ViT approaches are alternative extensions mentioned in the brief. They need not all be implemented; confirm your guide's expectations. Claim real-time operation only after measuring the full capture-to-prediction path.

## 12. Prepare the report, presentation, and viva

- [ ] Report sections: abstract, introduction, problem statement, objectives, literature survey, methodology, dataset/preprocessing, architecture, implementation, evaluation, discussion, limitations, conclusion, future work, and references.
- [ ] Include a system diagram: **network traffic / dataset → flow features → preprocessing → Transformer → attack classification → interface**.
- [ ] Include the label mapping, split procedure, architecture settings, learning curves, confusion matrices, comparison table, and demo screenshots.
- [ ] Explain the computer-networks contribution: what a flow represents, why traffic statistics help identify attacks, and where the IDS would sit in a network.
- [ ] Explain what your Transformer attends over and why that representation was chosen.
- [ ] Separate measured improvements from hoped-for improvements and distinguish your implementation contribution from published research novelty.
- [ ] Cite datasets, papers, software, and reused code; follow your institution's format.
- [ ] Prepare slides and a short demo video or screenshot backup.
- [ ] Prepare viva answers: why Transformer, why this dataset, why macro-F1, how leakage was avoided, how DoS differs from DDoS, what caused false positives, and what is required for live deployment.
- [ ] Include a README with environment setup, data preparation, training, evaluation, and demo commands.

**Finish this step with:** complete submission materials and a rehearsed demonstration.

## Suggested eight-week schedule

| Week | Main work | Checkpoint |
|---|---|---|
| 1 | Scope, networking concepts, literature, environment | Approved plan |
| 2 | Download, inspect, clean, map labels, split data | Data pipeline |
| 3 | Train traditional baselines | Initial metrics |
| 4 | Implement and train Transformer | Working checkpoint |
| 5 | Tune and complete required deep-model comparisons | Selected models |
| 6 | Final evaluation, ablation, error analysis | Results package |
| 7 | Interface and optional extension if time allows | Working demo |
| 8 | Report, slides, reproducibility, viva rehearsal | Submission package |

Adjust this schedule to your deadline. Start writing the report during development.

## Final submission checklist

- [ ] Source code and dependency file.
- [ ] README and instructions to obtain the dataset.
- [ ] Dataset citation, feature schema, label mapping, and split details.
- [ ] Saved preprocessing pipeline and selected model checkpoint.
- [ ] Baseline and Transformer results with plots.
- [ ] Working demo with sample input and prediction output.
- [ ] Final report, slides, and demo backup.
- [ ] Documented limitations and future work.

**First task to do now:** write the scope page and inspect a small CIC-IDS2017 CSV. Confirm its actual columns and labels before designing the model.

## Official starting references

- CIC-IDS2017 documentation and downloads: https://www.unb.ca/cic/datasets/ids-2017.html
- CIC dataset catalogue and usage/citation information: https://www.unb.ca/cic/datasets/index.html
- PyTorch TransformerEncoderLayer reference: https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoderLayer.html

References checked on 5 October 2026. Model settings and timetable are suggested starting points, not experimentally verified results.
