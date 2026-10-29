import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import torch
from nids.inference import Predictor
from nids.explain import explain_shap,explain_lime

def main():
    torch.set_num_threads(4)
    p=argparse.ArgumentParser();p.add_argument('--method',choices=['shap','lime'],default='shap')
    p.add_argument('--input',type=Path,default=Path('data/samples/demo_flows.csv'))
    p.add_argument('--row',type=int,default=0);p.add_argument('--output',type=Path,default=Path('results/explanations'))
    a=p.parse_args();model=Predictor('artifacts')
    background=pd.read_csv('data/processed/train_flows.csv').sample(100,random_state=42)
    row=pd.read_csv(a.input).iloc[[a.row]]
    # Impute the explainer inputs with training medians, before sampling perturbations.
    medians=pd.Series(model.preprocessor.named_steps['impute'].statistics_,index=model.metadata['features'])
    background=background.fillna(medians);row=row.fillna(medians)
    table,meta=(explain_shap if a.method=='shap' else explain_lime)(model,background,row)
    a.output.mkdir(parents=True,exist_ok=True);table.to_csv(a.output/f'{a.method}.csv',index=False)
    (a.output/f'{a.method}.json').write_text(json.dumps(meta,indent=2));print(meta)

if __name__=='__main__':main()
