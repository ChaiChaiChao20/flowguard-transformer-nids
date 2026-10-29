"""Bounded-memory audit, unique-flow sampling, and training-only preprocessing."""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from nids.preprocessing import build_preprocessor, numeric_features
from nids.schema import CLASSES, FEATURES, FEATURE_INFO, LABEL_MAP, EXTENDED_CLASSES, EXTENDED_LABEL_MAP


def main():
    global CLASSES, LABEL_MAP
    p = argparse.ArgumentParser()
    p.add_argument("--raw", type=Path, default=Path("data/raw"))
    p.add_argument("--output", type=Path, default=Path("data/processed"))
    p.add_argument("--per-class", type=int, default=3500)
    p.add_argument("--benign", type=int, default=5000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument('--extended',action='store_true',help='Add FTP/SSH brute force and infiltration classes')
    a = p.parse_args()
    if a.extended: CLASSES, LABEL_MAP = EXTENDED_CLASSES, EXTENDED_LABEL_MAP
    if min(a.per_class, a.benign) < 30:
        raise ValueError("Use at least 30 samples per class.")
    a.output.mkdir(parents=True, exist_ok=True)
    files = sorted(a.raw.glob("*.csv"))
    if not files:
        raise FileNotFoundError("No raw CSVs. Run scripts/download_data.py first.")
    rng = np.random.default_rng(a.seed)
    original = Counter()
    unique_counts = Counter()
    seen = {}
    conflicts = set()
    pools = {c: pd.DataFrame() for c in CLASSES}
    rows = excluded = duplicates = invalid_cells = infinite_cells = 0
    for file in files:
        offset = 0
        for chunk in pd.read_csv(file, chunksize=50000, encoding="utf-8-sig", low_memory=False):
            chunk.columns = chunk.columns.str.strip()
            if "Label" not in chunk:
                raise ValueError(f"Label is missing in {file.name}")
            original.update(chunk.Label.astype(str).str.strip())
            labels = chunk.Label.astype(str).str.strip().map(LABEL_MAP)
            supported = labels.notna()
            excluded += int((~supported).sum())
            x = numeric_features(chunk.loc[supported], strict=False)
            invalid_cells += int(x.isna().sum().sum())
            raw_num = chunk.loc[supported, FEATURES].apply(pd.to_numeric, errors="coerce")
            infinite_cells += int(np.isinf(raw_num.to_numpy()).sum())
            hashes = pd.util.hash_pandas_object(x, index=False).to_numpy()
            kept = []
            for i, (h, label) in enumerate(zip(hashes, labels.loc[supported])):
                key = int(h)
                if key in seen:
                    duplicates += 1
                    if seen[key] != label:
                        conflicts.add(key)
                else:
                    seen[key] = label
                    unique_counts[label] += 1
                    kept.append(i)
            chosen = x.iloc[kept].copy()
            chosen["target"] = labels.loc[supported].iloc[kept].to_numpy()
            chosen["original_label"] = chunk.loc[supported, "Label"].iloc[kept].astype(str).to_numpy()
            chosen["feature_hash"] = hashes[kept]
            chosen["source_file"] = file.name
            chosen["source_row"] = np.flatnonzero(supported.to_numpy())[kept] + offset + 2
            chosen["priority"] = rng.random(len(chosen))
            for cls in CLASSES:
                cap = a.benign if cls == "Benign" else a.per_class
                pools[cls] = pd.concat([pools[cls], chosen[chosen.target == cls]], ignore_index=True).nsmallest(cap, "priority")
            offset += len(chunk)
            rows += len(chunk)
        print(f"Audited {file.name}: {offset:,} rows", flush=True)
    data = pd.concat(pools.values(), ignore_index=True)
    selected_conflicts = int(data.feature_hash.isin(conflicts).sum())
    data = data[~data.feature_hash.isin(conflicts)].reset_index(drop=True)
    counts = data.target.value_counts().reindex(CLASSES, fill_value=0)
    if (counts < 20).any():
        raise ValueError(f"Insufficient unique examples for all classes: {counts.to_dict()}")
    indices = np.arange(len(data))
    train, holdout = train_test_split(indices, test_size=0.30, stratify=data.target, random_state=a.seed)
    validation, test = train_test_split(holdout, test_size=0.5, stratify=data.target.iloc[holdout], random_state=a.seed)
    pre = build_preprocessor()
    pre.fit(data.iloc[train][FEATURES])
    joblib.dump(pre, a.output / "preprocessor.joblib")
    arrays = {'class_names':np.array(CLASSES)}
    split_counts = {}
    manifests = []
    for split, ids in [("train", train), ("validation", validation), ("test", test)]:
        part = data.iloc[ids].copy()
        arrays[f"X_{split}"] = pre.transform(part[FEATURES]).astype("float32")
        arrays[f"y_{split}"] = part.target.map({c:i for i,c in enumerate(CLASSES)}).to_numpy(dtype="int64")
        split_counts[split] = part.target.value_counts().reindex(CLASSES).to_dict()
        manifest = part[["feature_hash", "source_file", "source_row", "original_label", "target"]].copy()
        manifest["split"] = split
        manifests.append(manifest)
        part.drop(columns="priority").to_csv(a.output / f"{split}_flows.csv", index=False)
    np.savez_compressed(a.output / "splits.npz", **arrays)
    pd.concat(manifests).to_csv(a.output / "split_manifest.csv", index=False)
    pd.DataFrame(FEATURE_INFO, columns=["feature", "unit", "description"]).to_csv(a.output / "feature_dictionary.csv", index=False)
    examples = data.iloc[test].groupby("target", sort=False).head(10)
    sample_root = a.output.parent / "samples"
    sample_root.mkdir(exist_ok=True)
    examples[FEATURES].to_csv(sample_root / "demo_flows.csv", index=False)
    examples[FEATURES + ["target"]].to_csv(sample_root / "demo_flows_labeled.csv", index=False)
    provenance = a.raw / "provenance.json"
    if provenance.exists():
        shutil.copy2(provenance, a.output / "provenance.json")
    stats = {
        "seed": a.seed, "original_rows": rows, "original_labels": dict(original),
        "excluded_unsupported_rows": excluded, "duplicate_feature_rows": duplicates,
        "conflicting_feature_hashes_removed": len(conflicts), "unique_supported_counts_before_conflict_removal": dict(unique_counts),
        "selected_conflicting_vectors_removed": selected_conflicts,
        "missing_or_nonfinite_feature_cells": invalid_cells, "infinite_feature_cells": infinite_cells,
        "sample_counts": counts.to_dict(), "splits": split_counts, "features": FEATURES,
        "classes": CLASSES, "label_map": LABEL_MAP,
        "split_strategy": "70/15/15 stratified random over unique selected-feature vectors, seed 42 by default",
        "sampling": "Uniform bottom-k random-priority sampling within class after selected-feature deduplication; conflicts subsequently removed",
        "limitations": ["Public mirror not independently byte-verified against original files", "Random split does not isolate sessions, devices or attack campaigns", "No temporal metadata in selected CSV inputs; no chronological generalization claim", "Class caps change prevalence; reported false-positive rate is on sampled benign flows"],
    }
    (a.output / "data_audit.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps({"sample_counts": stats["sample_counts"], "splits": split_counts}, indent=2), flush=True)


if __name__ == "__main__":
    main()
