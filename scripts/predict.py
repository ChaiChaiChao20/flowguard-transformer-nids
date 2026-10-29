import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import torch
from nids.inference import Predictor


def main():
    torch.set_num_threads(4)
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("predictions.csv"))
    p.add_argument("--artifacts", type=Path, default=Path("artifacts"))
    a = p.parse_args()
    result = Predictor(a.artifacts).predict(pd.read_csv(a.input))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(a.output, index=False)
    print(result.predicted_class.value_counts().to_string())
    print(f"Saved {len(result)} predictions to {a.output}")


if __name__ == "__main__":
    main()
