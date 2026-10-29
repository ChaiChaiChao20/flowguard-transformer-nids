import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd,torch
from nids.advanced_inference import AdvancedPredictor
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True)
p.add_argument('--model',default='TemporalTransformer');p.add_argument('--output',type=Path,default=Path('results/advanced_predictions.csv'))
a=p.parse_args();torch.set_num_threads(4)
result=AdvancedPredictor('artifacts/advanced',a.model).predict(pd.read_csv(a.input))
a.output.parent.mkdir(parents=True,exist_ok=True);result.to_csv(a.output,index=False);print(f'{len(result)} predictions saved to {a.output}')
