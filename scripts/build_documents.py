"""Build submission documents exclusively from recorded experiment artifacts."""
from datetime import datetime
from html import escape
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from nids.schema import CLASSES, FEATURES

ROOT = Path(__file__).resolve().parents[1]


def main():
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    audit = json.loads((ROOT / "data/processed/data_audit.json").read_text(encoding="utf-8"))
    meta = json.loads((ROOT / "artifacts/model_metadata.json").read_text(encoding="utf-8"))
    metrics = json.loads((ROOT / "results/test_metrics.json").read_text(encoding="utf-8"))
    validation = json.loads((ROOT / "results/validation_metrics.json").read_text(encoding="utf-8"))
    transformer = metrics["Transformer"]
    comparison = pd.read_csv(ROOT / "results/model_comparison.csv")
    winner = comparison.sort_values("macro_f1", ascending=False).iloc[0]
    report = transformer["classification_report"]
    sections = []

    def section(title, blocks):
        sections.append({"title": title, "blocks": blocks})

    def para(text):
        return {"type": "paragraph", "text": text}

    def table(headers, rows):
        return {"type": "table", "headers": headers, "rows": rows}

    def image(path, caption):
        return {"type": "image", "path": path, "caption": caption}

    section("1. Abstract and project scope", [
        para("This project implements FlowGuard, a flow-based network intrusion classification pipeline. A numeric feature-token Transformer predicts Benign, DoS, DDoS, Botnet, or Port Scan from 24 traffic statistics. The pipeline includes audited dataset preparation, training-only preprocessing, validation-selected checkpoints, seven-model comparisons, a local prediction dashboard, and reproducible artifacts."),
        para(f"The evaluated sample contains {sum(audit['sample_counts'].values()):,} unique selected-feature vectors from a public CIC-IDS2017 mirror. The split contains {meta['training_rows']:,} training, {meta['validation_rows']:,} validation, and {meta['test_rows']:,} test flows. The Transformer achieved test accuracy {transformer['accuracy']:.2%} and macro-F1 {transformer['macro_f1']:.4f}. The highest observed macro-F1 belongs to {winner['model']} ({winner['macro_f1']:.4f}). These findings apply to the sampled random-split benchmark, not live-network performance."),
        para("The supplied brief motivates self-attention, multi-class detection, comparison with CNN/LSTM/GRU and traditional machine learning, and eventual efficient deployment. This delivered version attends across features within one completed flow. It does not establish temporal sequence learning, zero-day detection, or live end-to-end operation."),
        table(["Scope", "Implemented decision"], [
            ["Input", "CICFlowMeter-compatible flow CSV, 24 numeric columns"],
            ["Output", "Five-class prediction, probabilities, attack flag"],
            ["Dataset", "Four pinned public-mirror CIC-IDS2017 CSV files"],
            ["Model", "Numeric feature-token Transformer encoder"],
            ["Demo", "Local Streamlit app and batch CLI"],
            ["Exclusions", "Raw packet ingestion, live capture, traffic blocking"],
        ]),
        para("Project identity: Computer Networks course project. Add the student/team name, registration number, institution, guide, and required declaration before submission. Faculty acceptance of scope and institutional formatting remains the student's responsibility."),
    ])
    section("2. Networking background and objectives", [
        para("A packet is an individual network transmission. A bidirectional flow groups packets belonging to a network exchange, typically identified by endpoint addresses, ports, and protocol. Forward and backward directions refer to the initiating and responding sides. A flow extractor aggregates counts, byte lengths, timing, and flags into one record."),
        para("DoS attempts to overwhelm a service, while DDoS involves multiple attacking sources. Botnet traffic originates from controlled hosts. Port scans probe services across ports or hosts. Within-flow statistics can help recognize recorded examples of these behaviors, but campaign-level patterns may require context across many flows. A flow-only model can therefore misinterpret traffic outside its training distribution."),
        para("Signature rules match known patterns. A supervised classifier learns associations between traffic features and known labels. Neither approach automatically guarantees coverage of novel attacks. The classifier developed here always returns a known class, including for inputs from an unknown distribution."),
        table(["Objective", "Evidence produced"], [
            ["Build a working Transformer NIDS", "Checkpoint, input contract, shared inference"],
            ["Classify multiple attacks", "Per-class precision/recall/F1 and confusion matrix"],
            ["Compare modeling approaches", "Seven models on identical features and splits"],
            ["Evaluate false alarms and efficiency", "Benign FPR and batched CPU inference timing"],
            ["Demonstrate usable predictions", "CSV upload, examples, export, sensitivity view"],
            ["Support reproduction", "Source, dependencies, data manifest, test checks"],
        ]),
        para("A possible network placement is a monitoring sensor receiving mirrored traffic, followed by a compatible flow extractor and the classifier. The delivered demo begins at the flow-CSV stage. Completed-flow detection also inherits collection/timeout delays, so model timing alone does not determine alert latency."),
    ])
    section("3. Related work and research position", [
        table(["Reference", "Contribution", "Use / boundary in this project"], [
            ["Vaswani et al., 2017 [1]", "Self-attention Transformer architecture", "Encoder building block; translation results do not imply IDS results"],
            ["Sharafaldin et al., 2018 [2]", "CIC-IDS2017 dataset and characterization", "Source dataset acknowledgement and flow-feature context"],
            ["Huang et al., 2020 [3]", "TabTransformer contextual categorical embeddings", "Related tabular attention work; our numeric tokenizer differs"],
            ["Gorishniy et al., 2021 [4]", "Strong tabular neural baselines and feature-token attention", "Motivates numeric tokens and comparisons with non-attention models"],
            ["Engelen et al., 2021 [5]", "CICIDS2017 construction and labeling issues", "Motivates dataset audit and limited generalization claims"],
            ["Ribeiro et al., 2016 [6]", "LIME local surrogate explanations", "Possible future extension, not the implemented sensitivity method"],
            ["Lundberg and Lee, 2017 [7]", "SHAP additive feature attribution", "Possible future extension, not a claimed project component"],
        ]),
        para("These sources motivate the approach and evaluation discipline. The brief's assertion that Transformers are underused is not accepted as a complete contemporary literature finding. This project implements a reproducible application of existing attention ideas to flow classification. It does not demonstrate a new Transformer architecture or establish publication-level novelty."),
        para("The central empirical question is whether a small feature-attention encoder produces competitive per-class performance relative to the implemented baselines under one fixed evaluation protocol. Random-split scores answer a restricted benchmark question; session-isolated and chronological tests are needed to assess deployment relevance."),
    ])
    section("4. Dataset acquisition, audit and labels", [
        para("CIC-IDS2017 provides labeled flow data relevant to the selected attacks [2]. Four machine-learning CSV files were acquired from the public repository c01dsnap/CIC-IDS2017, pinned to revision 4e9edfa727f800b6f595bc2ee7420527156562b2. The official download form returned a server error. Mirror revision, URLs, byte sizes, download time and SHA-256 checksums are recorded in provenance.json. The mirror was not independently byte-verified against original UNB files."),
        table(["Audit item", "Observed count"], [
            ["Original rows across four files", f"{audit['original_rows']:,}"],
            ["Unsupported-label rows excluded", f"{audit['excluded_unsupported_rows']:,}"],
            ["Repeated selected-feature vectors", f"{audit['duplicate_feature_rows']:,}"],
            ["Conflicting hashes identified and excluded", f"{audit['conflicting_feature_hashes_removed']:,}"],
            ["Selected conflicting vectors removed", str(audit['selected_conflicting_vectors_removed'])],
            ["Missing/non-finite selected-feature cells", f"{audit['missing_or_nonfinite_feature_cells']:,}"],
            ["Infinite selected-feature cells", f"{audit['infinite_feature_cells']:,}"],
        ]),
        table(["Project class", "Dataset label mapping", "Sampled flows"], [
            ["Benign", "BENIGN", str(audit['sample_counts']['Benign'])],
            ["DoS", "Hulk, GoldenEye, slowloris, Slowhttptest subtypes", str(audit['sample_counts']['DoS'])],
            ["DDoS", "DDoS", str(audit['sample_counts']['DDoS'])],
            ["Botnet", "Bot", str(audit['sample_counts']['Botnet'])],
            ["Port Scan", "PortScan", str(audit['sample_counts']['Port Scan'])],
        ]),
        para("Rows with unsupported attack labels are excluded, never mapped to Benign. Original labels remain in the split manifest. Numeric inputs exclude IP addresses, timestamps, flow IDs and ports. Before sampling, the pipeline hashes selected numeric feature vectors, removes duplicate vectors, and flags inconsistent labels for later removal. Uniform random-priority selection retains up to 5,000 Benign and 3,500 flows per attack class; fewer remain when a class has fewer unique vectors. Deduplication changes the population and removes repeated examples, which is documented rather than hidden."),
    ])
    section("5. Preprocessing and evaluation split", [
        para("Each source file is read in chunks of 50,000 rows. Column names receive whitespace normalization and selected fields receive numeric conversion. Infinity and missing numeric values become missing cells. Identical selected-feature vectors receive the same 64-bit pandas hash. A hash collision is theoretically possible; the integrity guarantee is specifically hash-based. Conflicting labels for the same hash are removed from the selected sample."),
        table(["Class", "Training", "Validation", "Test"], [[c, str(audit['splits']['train'][c]), str(audit['splits']['validation'][c]), str(audit['splits']['test'][c])] for c in CLASSES]),
        para("The sample receives a 70/15/15 stratified random split using seed 42. All splits contain all five classes and no selected feature hash occurs in more than one split. Because these CSV inputs do not provide the session information needed for the implemented grouping scheme, related flows or campaigns can still cross splits. Attacks occur in particular captures, so leaving out one day can also remove classes from training. No temporal or session-isolation claim is made."),
        para("The preprocessor learns per-feature medians from training data only, applies a signed logarithm g(x) = sign(x) log(1 + |x|), then fits training-only standardization z = (g(x) - training_mean) / training_std. Validation and test rows use these saved statistics. Constant features remain in the fixed schema. No oversampling, test-driven feature selection, or dataset-wide fitted normalization is used."),
        para("Neural loss weights equal the square root of N / (K * n_class), computed from the training counts. Traditional baselines use their balanced class-weight option. Class caps reduce compute cost and change prevalence; weighted-F1 and accuracy consequently describe this sample, while benign FPR describes its sampled benign flows."),
        para("The split manifest includes feature hash, source filename, original row number, original label, project label, and split. Raw sampled split CSVs and transformed arrays are included for reproduction. The feature dictionary documents all 24 names and units."),
    ])
    section("6. Transformer and comparison models", [
        para("For each standardized feature x_j, the model builds token e_j = x_j * w_j + b_j, with independently learned vectors w_j and b_j. The feature-specific bias represents feature identity. A learned CLS token is prepended. Two Transformer encoder layers connect all feature tokens through four-head self-attention. Layer normalization and a linear head map the final CLS representation to five logits. Cross-entropy consumes logits; softmax produces displayed probabilities."),
        table(["Transformer component", "Configuration"], [
            ["Feature tokens", "24 numeric features + 1 CLS token"],
            ["Embedding dimension", "32"], ["Encoder layers / attention heads", "2 / 4"],
            ["Feed-forward width / activation", "128 / GELU"], ["Dropout", "0.1"],
            ["Normalization", "Pre-norm encoder; final LayerNorm"],
            ["Trainable parameters", str(transformer['trainable_parameters'])],
        ]),
        para("Self-attention computes softmax(QK^T / sqrt(d_head))V. Its receptive field covers all selected features within a flow. This implementation neither tokenizes text nor loads pretrained BERT weights. It is a numeric feature-token encoder inspired by tabular Transformer research [4], rather than an exact replication of TabTransformer [3]."),
        table(["Baseline", "Declared configuration"], [
            ["Logistic Regression", "Balanced weights, max_iter 1200"],
            ["Random Forest", "120 trees, depth 18, min leaf 2, balanced weights"],
            ["MLP", "Two 128-wide hidden layers, GELU, dropout"],
            ["CNN", "Two 32-channel 1D convolutions, dense classifier"],
            ["LSTM / GRU", "48 hidden units, fixed-feature sequence, dense classifier"],
        ]),
        para("All models receive the same features and splits. Recurrent and convolutional models use a fixed feature order, not chronological observations. MLP supplies a non-attention reference, but architectures have different parameter counts, so the comparison is not a perfectly matched causal ablation of attention."),
    ])
    section("7. Training procedure and measured comparison", [
        para(f"The experiment uses seed {meta['seed']} and CPU training with {meta['hardware']['torch_threads']} PyTorch threads on a machine reporting {meta['hardware']['logical_cpus']} logical CPUs. Neural models use AdamW, learning rate 0.001, weight decay 0.0001, batch size 256, gradient clipping at norm 1, and at most {meta['training_config']['epochs_max']} epochs. Early stopping waits {meta['training_config']['early_stopping_patience']} epochs without improvement in validation macro-F1. Each neural checkpoint is the best validation checkpoint. One configuration per model was declared; no exhaustive tuning or multi-seed uncertainty estimate was performed."),
        table(["Model", "Accuracy", "Macro-F1", "Weighted-F1", "Benign FPR"], [[r.model, f"{r.accuracy:.2%}", f"{r.macro_f1:.4f}", f"{r.weighted_f1:.4f}", f"{r.benign_false_positive_rate:.2%}"] for r in comparison.itertuples()]),
        para(f"The best observed test macro-F1 was {winner['macro_f1']:.4f} for {winner['model']}. Transformer validation macro-F1 was {validation['Transformer']['macro_f1']:.4f}; its best epoch was {transformer['best_epoch']}. These comparisons reflect this implementation, dataset sample and training budget. They do not establish that any architecture is universally superior."),
        image("../results/plots/model_comparison.png", "Figure 1. Test macro-F1 for the seven fixed-configuration models."),
    ])
    section("8. Per-class findings and efficiency", [
        table(["Transformer class", "Precision", "Recall", "F1", "Support"], [[c, f"{report[c]['precision']:.4f}", f"{report[c]['recall']:.4f}", f"{report[c]['f1-score']:.4f}", str(int(report[c]['support']))] for c in CLASSES]),
        para("Macro-F1 averages the class F1 scores equally. Weighted-F1 weights them by test support. Benign false-positive rate equals benign flows predicted as any attack divided by all benign test flows. Confusion matrices identify specific category mix-ups. The error file preserves the actual features and source metadata of misclassified Transformer test flows."),
        image("../results/plots/Transformer_confusion.png", "Figure 2. Transformer test confusion matrix with actual counts."),
        para(f"The Transformer artifact contains {transformer['model_bytes']:,} bytes. Its training run took {transformer['training_seconds']:.2f} seconds, including validation passes. Median model-only inference time across three warmed CPU passes was {transformer['inference_ms_per_flow']:.4f} ms per flow, with neural batches up to 256. This timing excludes preprocessing, capture, flow completion and feature extraction. It is not an end-to-end alert-latency measurement."),
    ])
    section("9. Implementation, demo and verification", [
        table(["Module", "Responsibility"], [
            ["nids/schema.py", "Class labels, numeric feature contract, units"],
            ["nids/preprocessing.py", "Input validation and saved preprocessing"],
            ["nids/models.py", "Transformer, MLP, CNN, LSTM and GRU"],
            ["nids/inference.py", "Reload checkpoint and batch prediction"],
            ["scripts/download_data.py", "Pinned mirror download, resume, provenance"],
            ["scripts/prepare_data.py", "Audit, sample, split and save processed data"],
            ["scripts/train.py", "Train, validate, evaluate, record metrics/plots"],
            ["app.py", "Local CSV classification and evidence dashboard"],
        ]),
        para("The app provides included held-out flows or CSV upload, previews input, validates the schema, predicts classes, shows distributions, exports all probabilities, and displays recorded comparison evidence. It uses the same Predictor class as the CLI. A separate ground-truth sample supports demonstration evaluation; labels are never part of the prediction feature matrix."),
        para("The local sensitivity view replaces one feature at a time with its training median and measures the change in the originally predicted class probability. Positive differences indicate that replacement reduced that score. Correlated features and unrealistic replacements can distort this probe. It is explicitly not SHAP, LIME, or a causal attribution."),
        para("Automated checks cover feature-column reordering, ignored labels, missing-column rejection, invalid-string/all-missing-row rejection, fixed imputer statistics, all-class output shapes, split hash disjointness and class coverage, medians matching training data, freshly loaded checkpoint predictions matching saved test evaluation, and finite sensitivity outputs. Actual check outcomes are stored in results/VERIFICATION.txt. The dashboard is also exercised with Streamlit's application test API."),
        para("The distribution includes measured metrics and model artifacts, so no accuracy figure is invented. A dependency lock file supports repeating the environment. Users obtain full raw data through the downloader rather than requiring the large source files in the package."),
    ])
    section("10. Discussion, limitations and conclusion", [
        para(f"The implemented pipeline successfully connects auditable flow data, feature attention, saved checkpoints and a local user interface. Under the declared benchmark, the Transformer reached {transformer['macro_f1']:.4f} macro-F1 and {transformer['benign_false_positive_rate']:.2%} benign FPR. {winner['model']} had the strongest observed macro-F1, so the report retains that finding rather than assuming the project title implies a Transformer win."),
        para("The main limitations are public-mirror provenance, historical dataset quality, sampling and deduplication changing prevalence, related sessions crossing random splits, one seed and configuration per model, and no external validation. The input removes direct identifiers but this does not eliminate all shortcut learning. A closed-set classifier cannot identify unseen categories reliably, and high probabilities can accompany incorrect or out-of-distribution predictions."),
        para("The supplied brief's goals of long-range temporal modeling, reduced false positives and real-time deployment require further evidence. This model evaluates feature relationships within flows. Actual temporal sequence modeling would require timestamped flow ordering, an explicit session/window definition, and nonoverlapping split construction. Real-time operation would require compatible live extraction, flow timeout settings, queue monitoring, and measured capture-to-prediction latency."),
        para("Future work should first test stronger session/time separation with class coverage, repeated seeds and a broader comparable validation search. Next steps are probability calibration, external-schema validation, unknown-distribution rejection, and feature-explanation methods with fidelity checks. Only then should a live extractor be integrated and benchmarked. Federated, graph, online-learning and ViT variants remain optional separate extensions."),
        para("The project's defensible contribution is a complete reproducible offline NIDS prototype and its measured evaluation. It demonstrates how to implement feature self-attention for multi-class attack classification while retaining the evidence and limitations needed to assess the outcome."),
        image("../results/plots/learning_curves.png", "Figure 3. Validation checkpoint histories and Transformer learning curves."),
    ])
    refs = [
        "[1] Vaswani et al. Attention Is All You Need. 2017. https://arxiv.org/abs/1706.03762",
        "[2] Sharafaldin, Lashkari and Ghorbani. Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization. ICISSP, 2018. Dataset: https://www.unb.ca/cic/datasets/ids-2017.html",
        "[3] Huang, Khetan, Cvitkovic and Karnin. TabTransformer: Tabular Data Modeling Using Contextual Embeddings. 2020. https://arxiv.org/abs/2012.06678",
        "[4] Gorishniy, Rubachev, Khrulkov and Babenko. Revisiting Deep Learning Models for Tabular Data. 2021. https://arxiv.org/abs/2106.11959",
        "[5] Engelen, Rimmer and Joosen. Troubleshooting an Intrusion Detection Dataset: the CICIDS2017 Case Study. IEEE SPW, 2021. https://intrusion-detection.distrinet-research.be/WTMC2021/tools_datasets.html",
        "[6] Ribeiro, Singh and Guestrin. Why Should I Trust You?: Explaining the Predictions of Any Classifier. 2016. https://arxiv.org/abs/1602.04938",
        "[7] Lundberg and Lee. A Unified Approach to Interpreting Model Predictions. 2017. https://arxiv.org/abs/1705.07874",
        "[8] PyTorch TransformerEncoderLayer documentation. https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoderLayer.html",
        "[9] Download mirror, pinned revision: https://huggingface.co/datasets/c01dsnap/CIC-IDS2017/tree/4e9edfa727f800b6f595bc2ee7420527156562b2",
    ]
    section("11. References and reproducibility record", [para(x) for x in refs] + [
        table(["Environment", "Recorded value"], [[k,v] for k,v in meta["versions"].items()]),
        para("Exact package versions appear in requirements-lock.txt. Per-file checksums appear in data/processed/provenance.json. Split source-row lineage appears in split_manifest.csv. Run arguments appear in results/run_config.json. Raw test predictions and error examples are available for independent inspection. No result in this report is an estimate of production-network performance."),
    ])
    content = {"title": meta["project"], "subtitle": "FlowGuard | Implementation and measured evaluation", "sections": sections}
    (docs / "report_content.json").write_text(json.dumps(content, indent=2), encoding="utf-8")
    md = ["# " + content["title"], "", content["subtitle"], ""]
    for section_data in sections:
        md.extend(["## " + section_data["title"], ""])
        for block in section_data["blocks"]:
            if block["type"] == "paragraph":
                md.extend([block["text"], ""])
            elif block["type"] == "table":
                md.extend(["| " + " | ".join(block["headers"]) + " |", "| " + " | ".join(["---"]*len(block["headers"])) + " |"])
                md.extend("| " + " | ".join(row) + " |" for row in block["rows"])
                md.append("")
            elif block["type"] == "image":
                md.extend([f"![{block['caption']}]({block['path']})", "", block["caption"], ""])
    (docs / "PROJECT_REPORT.md").write_text("\n".join(md), encoding="utf-8")
    slides = [
        {"title": "Transformer-Based Network Intrusion Detection System", "subtitle": "Intelligent Multi-Class Cyber Attack Classification", "body": ["FlowGuard", "Computer Networks Project"], "notes": "Use the exact assigned title shown here. Add personal and institutional details before submission."},
        {"title": "Problem and scope", "body": ["Classify completed network flows into Benign, DoS, DDoS, Botnet or Port Scan.", "Use 24 traffic statistics with feature self-attention.", "Compare seven models on the same dataset split.", "Demonstrate predictions in a local CSV application."], "notes": "Scope follows the supplied project brief. This implementation is offline and feature-based. It does not establish zero-day or temporal sequence detection."},
        {"title": "Networking inputs", "body": ["Flow duration and forward/backward packet counts", "Packet-length means, maxima and variation", "Byte throughput and packet rates", "Packet inter-arrival statistics and TCP flags", "Input contract excludes IPs, timestamps, IDs and ports"], "notes": "Feature names and units: data/processed/feature_dictionary.csv. Matching extraction semantics are required for new traffic."},
        {"title": "Dataset and split", "body": [f"{audit['original_rows']:,} source rows audited from four CIC-IDS2017 mirror CSVs", f"{sum(audit['sample_counts'].values()):,} selected unique feature vectors", f"Training {meta['training_rows']:,} / validation {meta['validation_rows']:,} / test {meta['test_rows']:,}", "Remove vector duplicates and conflicting labels before splitting", "Fit all preprocessing statistics on training rows only"], "notes": "Source: https://www.unb.ca/cic/datasets/ids-2017.html and pinned mirror provenance.json. Random split can retain related sessions. Class caps alter prevalence. Mirror not independently byte-verified."},
        {"title": "Transformer architecture", "body": ["24 numeric feature tokens with learned feature identities", "One learned CLS token", "Embedding dimension 32, four heads, two encoder layers", "CLS representation with a five-class linear head", "Attention connects features within one flow"], "notes": "Own implementation in nids/models.py. Inspired by https://arxiv.org/abs/2106.11959. It is not pretrained BERT or an exact TabTransformer implementation. No temporal flow sequences."},
        {"title": "Training and comparison protocol", "body": ["Logistic Regression, Random Forest, MLP, CNN, LSTM, GRU and Transformer", "AdamW with learning rate 0.001 and batch size 256", "Weighted cross-entropy and validation macro-F1 checkpoint selection", f"At most {meta['training_config']['epochs_max']} epochs, one configuration and seed per model", "CNN/LSTM/GRU use fixed feature order"], "notes": "Exact configs in model_metadata.json and run_config.json. Baselines have different parameter counts. One configuration per model limits conclusions about architecture superiority."},
        {"title": "Measured model comparison", "chart": {"categories": comparison.model.tolist(), "values": comparison.macro_f1.tolist()}, "subtitle": f"Highest observed macro-F1: {winner['model']} ({winner['macro_f1']:.4f})", "notes": "Own measured results: results/model_comparison.csv. Test macro-F1 on sampled random-split flows. No live/generalization claim."},
        {"title": "Transformer findings", "body": [f"Test accuracy: {transformer['accuracy']:.2%}", f"Test macro-F1: {transformer['macro_f1']:.4f}", f"Benign false-positive rate: {transformer['benign_false_positive_rate']:.2%}", f"Best validation checkpoint: epoch {transformer['best_epoch']}", f"CPU model inference: {transformer['inference_ms_per_flow']:.4f} ms per flow"], "notes": "Own results/test_metrics.json. Timing excludes capture, feature extraction and preprocessing. Inspect per-class recall and error flows as well as accuracy."},
        {"title": "Working demonstration", "body": ["CSV upload or 50 included held-out flows", "Five-class predictions and probability scores", "Class distribution and downloadable results", "Recorded confusion matrices and model comparison", "Median-replacement feature sensitivity"], "notes": "Run app.py using README. Sensitivity probe is not SHAP/LIME or causal attribution. Scores are uncalibrated probabilities. Actual classes are stored separately from demo input."},
        {"title": "Limitations and next steps", "body": ["Related sessions may cross random splits", "One seed and configuration per architecture", "Historical public-mirror sample with modified prevalence", "Temporal modeling and live extraction require additional work", "Next: stronger splits, external validation and calibration"], "notes": "Dataset-quality source: Engelen et al., https://intrusion-detection.distrinet-research.be/WTMC2021/tools_datasets.html. The present model chooses from known classes only."},
        {"title": "Conclusion and references", "body": ["Delivered a reproducible flow-classification pipeline and local dashboard.", f"{winner['model']} achieved the highest macro-F1 in the declared experiment.", "Claims follow measured results and documented evaluation limits.", "Key references: Vaswani, Sharafaldin, Gorishniy and Engelen."], "notes": "Full bibliography: docs/PROJECT_REPORT.md. https://arxiv.org/abs/1706.03762 ; https://www.unb.ca/cic/datasets/ids-2017.html ; https://arxiv.org/abs/2106.11959 ; https://intrusion-detection.distrinet-research.be/WTMC2021/tools_datasets.html"},
    ]
    (docs / "slide_content.json").write_text(json.dumps(slides, indent=2), encoding="utf-8")
    html_slides = []
    for i, slide in enumerate(slides):
        body = "<ul>" + "".join("<li>"+escape(x)+"</li>" for x in slide.get("body",[])) + "</ul>"
        if "chart" in slide:
            body = '<img src="../results/plots/model_comparison.png" alt="Measured model comparison">'
        html_slides.append(f'<section><small>COMPUTER NETWORKS PROJECT</small><h1>{escape(slide["title"])}</h1><p class="sub">{escape(slide.get("subtitle",""))}</p>{body}<footer>{i+1} / {len(slides)}</footer></section>')
    html = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>FlowGuard Project Presentation</title><style>
body{margin:0;background:#0d172a;font-family:Arial,sans-serif;color:#edf5ff}section{min-height:82vh;padding:7vh 8vw;border-bottom:1px solid #355071;box-sizing:border-box;position:relative}small{color:#85b9ff;letter-spacing:2px}h1{font-size:46px;max-width:1100px}li{font-size:27px;line-height:1.65;max-width:1050px;margin-bottom:12px}.sub{font-size:24px;color:#a9c9ed}footer{color:#85b9ff;margin-top:35px}img{max-width:850px;width:80%;background:white} @media print{section{page-break-after:always;height:100vh}body{background:white;color:#14233c}li{font-size:23px}}
</style></head><body>"""+"".join(html_slides)+"</body></html>"
    (docs / "PRESENTATION.html").write_text(html, encoding="utf-8")
    print("Generated report source, report content, slide content and browser presentation.")
    if (ROOT / 'artifacts/advanced/model_metadata.json').exists():
        import build_extension_documents
        build_extension_documents.main()


if __name__ == "__main__":
    main()
