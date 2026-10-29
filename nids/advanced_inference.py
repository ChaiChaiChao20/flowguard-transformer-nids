import json
from pathlib import Path
import joblib,numpy as np,pandas as pd,torch
from .advanced_models import build_advanced
from .context import context_features,categorical_features,flow_adjacency,temporal_windows


class AdvancedPredictor:
    def __init__(self,root,name='TemporalTransformer'):
        root=Path(root);self.metadata=json.loads((root/'model_metadata.json').read_text())
        if name not in self.metadata['models']:raise ValueError('Model not trained: '+name)
        self.name=name;self.classes=self.metadata['classes']
        architecture=self.metadata['models'][name].get('architecture',name)
        self.model=build_advanced(architecture,len(self.metadata['features']),len(self.classes))
        self.model.load_state_dict(torch.load(root/f'{name}.pt',map_location='cpu',weights_only=True));self.model.eval()
        self.preprocessor=joblib.load(root/'preprocessor.joblib')

    def predict(self,frame):
        frame=frame.reset_index(drop=True).copy();values=self.preprocessor.transform(context_features(frame)).astype('float32')
        if not np.isfinite(values).all():raise ValueError('Invalid context preprocessing output')
        endpoints=np.arange(len(frame));x=torch.from_numpy(values)
        if self.name=='TemporalTransformer':
            if 'Timestamp' not in frame:raise ValueError('Timestamp required for chronological inference')
            frame['time']=pd.to_datetime(frame.Timestamp,dayfirst=True,format='mixed',errors='raise')
            frame['split']='inference';seq,endpoints,_=temporal_windows(frame,values)
            x=torch.from_numpy(seq)
        probabilities=[]
        with torch.inference_mode():
            for ids in torch.arange(len(x)).split(128):
                if self.name=='TabTransformer':logits=self.model(x[ids],torch.from_numpy(categorical_features(frame.iloc[ids.numpy()])))
                elif self.name=='FlowGraphNetwork':logits=self.model(x[ids],torch.from_numpy(flow_adjacency(frame.iloc[ids.numpy()])))
                else:logits=self.model(x[ids])
                probabilities.append(logits.softmax(-1).numpy())
        probs=np.concatenate(probabilities);indices=probs.argmax(1)
        result=pd.DataFrame({'input_row':endpoints+1,'predicted_class':np.array(self.classes)[indices],
                             'model_probability':probs.max(1),'is_attack':indices!=0})
        for i,c in enumerate(self.classes):result['probability_'+c.replace(' ','_')]=probs[:,i]
        return result
