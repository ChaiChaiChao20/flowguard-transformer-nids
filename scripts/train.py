"""Train fixed-config baselines and attention model; select epochs on validation only."""
import argparse
import copy
import json
import os
from pathlib import Path
import platform
import random
import shutil
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from nids.models import build_model
from nids.schema import CLASSES, FEATURES


def probabilities(model, x, batch=256):
    model.eval()
    with torch.inference_mode():
        return np.concatenate([model(torch.from_numpy(x[i:i+batch])).softmax(-1).numpy()
                               for i in range(0, len(x), batch)])


def metrics(y, predicted):
    normal = y == 0
    return {"accuracy": float(accuracy_score(y, predicted)),
            "macro_f1": float(f1_score(y, predicted, average="macro", zero_division=0)),
            "weighted_f1": float(f1_score(y, predicted, average="weighted", zero_division=0)),
            "benign_false_positive_rate": float((predicted[normal] != 0).mean()),
            "classification_report": classification_report(y, predicted, labels=list(range(len(CLASSES))),
                                                           target_names=CLASSES, zero_division=0, output_dict=True),
            "confusion_matrix": confusion_matrix(y, predicted, labels=list(range(len(CLASSES)))).tolist()}


def confusion_plot(y, pred, name, root):
    matrix = confusion_matrix(y, pred, labels=list(range(len(CLASSES))))
    for normalized in [False, True]:
        values = matrix / np.maximum(matrix.sum(axis=1, keepdims=True), 1) if normalized else matrix
        fig, ax = plt.subplots(figsize=(7.5, 6))
        im = ax.imshow(values, cmap="Blues")
        ax.set(xticks=range(len(CLASSES)), yticks=range(len(CLASSES)),
               xticklabels=CLASSES, yticklabels=CLASSES, xlabel="Predicted class", ylabel="Actual class",
               title=f"{name} | {'row-normalized' if normalized else 'counts'}")
        for i in range(len(CLASSES)):
            for j in range(len(CLASSES)):
                ax.text(j, i, f"{values[i,j]:.2f}" if normalized else str(matrix[i,j]),
                        ha="center", va="center", color="white" if values[i,j] > values.max()/2 else "black")
        fig.colorbar(im, ax=ax)
        fig.tight_layout()
        fig.savefig(root / f"{name}_confusion{'_normalized' if normalized else ''}.png", dpi=160)
        plt.close(fig)


def main():
    global CLASSES
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=Path("data/processed"))
    p.add_argument("--artifacts", type=Path, default=Path("artifacts"))
    p.add_argument("--results", type=Path, default=Path("results"))
    p.add_argument("--epochs", type=int, default=18)
    p.add_argument("--patience", type=int, default=5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--models", nargs="+", default=["LogisticRegression", "RandomForest", "MLP", "CNN", "LSTM", "GRU", "Transformer"])
    a = p.parse_args()
    if a.epochs < 1 or a.patience < 1:
        raise ValueError("Epochs and patience must be positive.")
    a.artifacts.mkdir(parents=True, exist_ok=True)
    a.results.mkdir(parents=True, exist_ok=True)
    plots = a.results / "plots"
    plots.mkdir(exist_ok=True)
    torch.set_num_threads(a.threads)
    torch.use_deterministic_algorithms(True)
    arrays = np.load(a.data / "splits.npz")
    if 'class_names' in arrays: CLASSES=arrays['class_names'].tolist()
    xt, yt = arrays["X_train"], arrays["y_train"]
    xv, yv = arrays["X_validation"], arrays["y_validation"]
    xe, ye = arrays["X_test"], arrays["y_test"]
    config = {"dim": 32, "heads": 4, "layers": 2, "dropout": 0.1}
    neural = {"epochs_max": a.epochs, "early_stopping_patience": a.patience,
              "optimizer": "AdamW", "learning_rate": 0.001, "weight_decay": 0.0001, "batch_size": 256,
              "loss": "CrossEntropyLoss with sqrt inverse training frequency weights",
              "selection_metric": "validation macro-F1", "tuning": "One predeclared configuration per model; no test-driven tuning"}
    summary = []
    details = {}
    validation_details = {}
    histories = {}
    train_count = np.bincount(yt, minlength=len(CLASSES))
    weight = np.sqrt(len(yt)/(len(CLASSES)*train_count)).astype("float32")
    for name in a.models:
        random.seed(a.seed)
        np.random.seed(a.seed)
        torch.manual_seed(a.seed)
        print(f"Training {name}...", flush=True)
        start = time.perf_counter()
        best_epoch = None
        parameter_count = None
        if name in {"LogisticRegression", "RandomForest"}:
            if name == "LogisticRegression":
                model = LogisticRegression(max_iter=1200, class_weight="balanced", random_state=a.seed)
            else:
                model = RandomForestClassifier(n_estimators=120, max_depth=18, min_samples_leaf=2,
                                               class_weight="balanced", random_state=a.seed, n_jobs=a.threads)
            model.fit(xt, yt)
            model_path = a.artifacts / f"{name}.joblib"
            joblib.dump(model, model_path)
            predict_probs = model.predict_proba
        else:
            model = build_model(name, len(FEATURES), len(CLASSES), **config)
            parameter_count = sum(v.numel() for v in model.parameters())
            optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.0001)
            loss_fn = nn.CrossEntropyLoss(weight=torch.from_numpy(weight))
            loader = DataLoader(TensorDataset(torch.from_numpy(xt), torch.from_numpy(yt)), batch_size=256, shuffle=True)
            best, state, stale, history = -1.0, None, 0, []
            for epoch in range(1, a.epochs+1):
                model.train()
                train_loss = 0.0
                for xb, yb in loader:
                    optimizer.zero_grad(set_to_none=True)
                    loss = loss_fn(model(xb), yb)
                    loss.backward()
                    nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    optimizer.step()
                    train_loss += loss.item()*len(xb)
                vp = probabilities(model, xv)
                vf = float(f1_score(yv, vp.argmax(1), average="macro", zero_division=0))
                vl = float(loss_fn(torch.from_numpy(np.log(np.maximum(vp, 1e-12))), torch.from_numpy(yv)))
                history.append({"epoch": epoch, "training_loss": train_loss/len(xt), "validation_loss": vl, "validation_macro_f1": vf})
                print(f"  {name} epoch {epoch:02d}: loss={train_loss/len(xt):.4f}, validation macro-F1={vf:.4f}", flush=True)
                if vf > best + 1e-6:
                    best, state, stale, best_epoch = vf, copy.deepcopy(model.state_dict()), 0, epoch
                else:
                    stale += 1
                if stale >= a.patience:
                    break
            model.load_state_dict(state)
            model_path = a.artifacts / f"{name}.pt"
            torch.save(model.state_dict(), model_path)
            histories[name] = history
            pd.DataFrame(history).to_csv(a.results / f"{name}_training_history.csv", index=False)
            predict_probs = lambda x, m=model: probabilities(m, x)
        training_seconds = time.perf_counter() - start
        val_pred = predict_probs(xv).argmax(1)
        validation_details[name] = metrics(yv, val_pred)
        # Freeze model before test access. No further selection uses test results.
        for _ in range(3):
            predict_probs(xe[:min(256, len(xe))])
        timings = []
        for _ in range(3):
            t = time.perf_counter()
            test_probs = predict_probs(xe)
            timings.append(time.perf_counter()-t)
        test_pred = test_probs.argmax(1)
        result = metrics(ye, test_pred)
        result.update({"training_seconds": training_seconds, "best_epoch": best_epoch,
                       "trainable_parameters": parameter_count, "model_bytes": model_path.stat().st_size,
                       "inference_ms_per_flow": float(np.median(timings)/len(xe)*1000),
                       "timing_scope": "CPU model prediction only; batches up to 256 for neural models, excludes preprocessing/capture"})
        details[name] = result
        summary.append({"model": name, **{k: result[k] for k in ["accuracy", "macro_f1", "weighted_f1", "benign_false_positive_rate", "training_seconds", "inference_ms_per_flow", "model_bytes", "best_epoch", "trainable_parameters"]}})
        confusion_plot(ye, test_pred, name, plots)
        predictions = pd.DataFrame({"actual_class": np.array(CLASSES)[ye], "predicted_class": np.array(CLASSES)[test_pred],
                                    "model_probability": test_probs.max(1), "test_row": np.arange(len(ye))})
        predictions.to_csv(a.results / f"{name}_test_predictions.csv", index=False)
        if name == "Transformer":
            raw_test = pd.read_csv(a.data / "test_flows.csv")
            errors = raw_test.loc[test_pred != ye].copy()
            errors["predicted_class"] = np.array(CLASSES)[test_pred[test_pred != ye]]
            errors["model_probability"] = test_probs.max(1)[test_pred != ye]
            errors.to_csv(a.results / "Transformer_misclassified_flows.csv", index=False)
        print(f"Completed {name}: test macro-F1={result['macro_f1']:.4f}", flush=True)
        # Preserve progress if later models fail.
        pd.DataFrame(summary).to_csv(a.results / "model_comparison.csv", index=False)
        (a.results / "test_metrics.json").write_text(json.dumps(details, indent=2), encoding="utf-8")
        (a.results / "validation_metrics.json").write_text(json.dumps(validation_details, indent=2), encoding="utf-8")
    shutil.copy2(a.data / "preprocessor.joblib", a.artifacts / "preprocessor.joblib")
    metadata = {"project": "Transformer-Based Network Intrusion Detection System for Intelligent Multi-Class Cyber Attack Classification",
                "representation": "24 numeric feature tokens plus CLS token; attention within individual flows",
                "features": FEATURES, "classes": CLASSES, "transformer_config": config,
                "training_config": neural, "seed": a.seed,
                "hardware": {"platform": platform.platform(), "processor": platform.processor(), "logical_cpus": os.cpu_count(), "torch_threads": a.threads, "device": "CPU"},
                "versions": {"python": platform.python_version(), "torch": torch.__version__, "sklearn": sklearn.__version__, "numpy": np.__version__, "pandas": pd.__version__},
                "training_rows": len(xt), "validation_rows": len(xv), "test_rows": len(xe),
                "limitations": ["This feature encoder is not the separate TemporalTransformer", "Sampled random split; correlated sessions may remain", "Closed-set classification; anomaly flags do not prove zero-day detection", "Recorded-flow classifier; live extraction and target-network accuracy need separate validation", "Model scores are not calibrated confidence", "Single seed/configuration; not an exhaustive architecture benchmark"]}
    (a.artifacts / "model_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(9, 5))
    table = pd.DataFrame(summary)
    ax.bar(table.model, table.macro_f1, color=["#94a3b8" if n != "Transformer" else "#2563eb" for n in table.model])
    ax.set(ylabel="Test macro-F1", ylim=(0,1.05), title="Fixed-configuration comparison on held-out sampled flows")
    ax.tick_params(axis="x", labelrotation=20)
    fig.tight_layout()
    fig.savefig(plots / "model_comparison.png", dpi=160)
    plt.close(fig)
    if histories:
        fig, axes = plt.subplots(1,2, figsize=(11,4))
        for name, history in histories.items():
            h = pd.DataFrame(history)
            axes[0].plot(h.epoch, h.validation_macro_f1, label=name)
        axes[0].set(xlabel="Epoch", ylabel="Validation macro-F1", title="Checkpoint selection")
        axes[0].legend()
        if "Transformer" in histories:
            h = pd.DataFrame(histories["Transformer"])
            axes[1].plot(h.epoch, h.training_loss, label="Training")
            axes[1].plot(h.epoch, h.validation_loss, label="Validation")
            axes[1].set(xlabel="Epoch", ylabel="Weighted cross-entropy", title="Transformer learning curves")
            axes[1].legend()
        fig.tight_layout()
        fig.savefig(plots / "learning_curves.png", dpi=160)
        plt.close(fig)
    (a.results / "run_config.json").write_text(json.dumps(vars(a), default=str, indent=2), encoding="utf-8")
    print("Saved checkpoints, test/validation metrics, predictions and plots.", flush=True)


if __name__ == "__main__":
    main()
