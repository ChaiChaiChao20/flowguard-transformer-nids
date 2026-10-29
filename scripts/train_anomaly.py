"""Benign-trained anomaly score, with validation-only false-alert threshold.

Unknown flag means atypical relative to training benign flows, not proven zero-day.
"""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import joblib,numpy as np,pandas as pd
from sklearn.ensemble import IsolationForest
root=Path(__file__).resolve().parents[1];data=np.load(root/'data/extended/processed/splits.npz')
model=IsolationForest(n_estimators=150,random_state=42,n_jobs=4)
model.fit(data['X_train'][data['y_train']==0])
validation=-model.score_samples(data['X_validation'][data['y_validation']==0])
threshold=float(np.quantile(validation,.99))
scores=-model.score_samples(data['X_test']);flag=scores>threshold;truth=data['y_test']!=0
result={'method':'IsolationForest fit on training benign flows only','threshold':threshold,
        'threshold_selection':'99th percentile of validation benign anomaly score',
        'test_benign_false_alert_rate':float(flag[~truth].mean()),
        'test_known_attack_anomaly_recall':float(flag[truth].mean()),
        'limitation':'Known dataset attacks only; no zero-day validation or claim'}
joblib.dump({'model':model,'threshold':threshold},root/'artifacts/extended/anomaly.joblib')
(root/'results/extended/anomaly_metrics.json').write_text(json.dumps(result,indent=2))
pd.DataFrame({'anomaly_score':scores,'atypical_flag':flag,'actual_attack':truth}).to_csv(root/'results/extended/anomaly_predictions.csv',index=False)
print(json.dumps(result,indent=2))
