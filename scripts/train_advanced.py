"""Train all optional architectures and measured adaptation simulations."""
import argparse,copy,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import joblib,numpy as np,pandas as pd,torch
from sklearn.metrics import accuracy_score,f1_score,classification_report,confusion_matrix
from nids.advanced_models import build_advanced
from nids.context import CONTEXT_FEATURES,categorical_features,flow_adjacency
from nids.adaptation import fedavg,local_update,PageHinkley

def score(y,pred,classes):
    return {'accuracy':float(accuracy_score(y,pred)),
        'macro_f1':float(f1_score(y,pred,labels=range(len(classes)),average='macro',zero_division=0)),
        'benign_false_positive_rate':float((pred[y==0]!=0).mean()) if (y==0).any() else None,
        'classification_report':classification_report(y,pred,labels=range(len(classes)),target_names=classes,output_dict=True,zero_division=0),
        'confusion_matrix':confusion_matrix(y,pred,labels=range(len(classes))).tolist(),
        'test_rows':len(y)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=Path('data/temporal'))
    p.add_argument('--artifacts',type=Path,default=Path('artifacts/advanced'))
    p.add_argument('--results',type=Path,default=Path('results/advanced'))
    p.add_argument('--epochs',type=int,default=10);a=p.parse_args()
    torch.set_num_threads(4);torch.manual_seed(42);np.random.seed(42)
    a.artifacts.mkdir(parents=True,exist_ok=True);a.results.mkdir(parents=True,exist_ok=True)
    data=np.load(a.data/'splits.npz');classes=data['class_names'].tolist()
    frames={s:pd.read_csv(a.data/f'{s}_flows.csv') for s in ['train','validation','test']}
    cat={s:torch.from_numpy(categorical_features(f)) for s,f in frames.items()}
    x={s:torch.from_numpy(data['X_'+s]) for s in frames};y={s:torch.from_numpy(data['y_'+s]) for s in frames}
    sx={s:torch.from_numpy(data['sequence_'+s]) for s in frames};sy={s:torch.from_numpy(data['sequence_y_'+s]) for s in frames}
    results={};histories={};metadata={'classes':classes,'features':CONTEXT_FEATURES,'models':{},'seed':42,
        'training':'fixed 10 epoch maximum, AdamW lr=.001, batch128, early-stop4, validation macro-F1',
        'graph_batch':128,'temporal_window':8,'temporal_max_gap_seconds':300}
    def forward(model,name,split,ids):
        if name=='TemporalTransformer':return model(sx[split][ids])
        if name=='TabTransformer':return model(x[split][ids],cat[split][ids])
        if name=='FlowGraphNetwork':return model(x[split][ids],torch.from_numpy(flow_adjacency(frames[split].iloc[ids.numpy()])))
        return model(x[split][ids])
    def predict(model,name,split):
        model.eval();n=len(sy[split]) if name=='TemporalTransformer' else len(y[split])
        if n==0:raise ValueError('No windows in '+split)
        with torch.inference_mode():return np.concatenate([forward(model,name,split,ids).softmax(-1).numpy() for ids in torch.arange(n).split(128)])
    for name in ['BERTStyleEncoder','TabTransformer','FlowViT','FlowGraphNetwork','TemporalTransformer']:
        torch.manual_seed(42);model=build_advanced(name,len(CONTEXT_FEATURES),len(classes))
        target=sy if name=='TemporalTransformer' else y
        counts=torch.bincount(target['train'],minlength=len(classes)).clamp_min(1)
        weight=torch.sqrt(len(target['train'])/(len(classes)*counts))
        lossfn=torch.nn.CrossEntropyLoss(weight=weight);opt=torch.optim.AdamW(model.parameters(),lr=.001)
        best=-1.;stale=0;history=[];start=time.perf_counter();state=None
        for epoch in range(1,a.epochs+1):
            model.train();total=0.;n=len(target['train'])
            ids=torch.arange(n) if name=='FlowGraphNetwork' else torch.randperm(n)
            for batch in ids.split(128):
                opt.zero_grad();loss=lossfn(forward(model,name,'train',batch),target['train'][batch]);loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(),1);opt.step();total+=loss.item()*len(batch)
            vp=predict(model,name,'validation');vf=f1_score(target['validation'].numpy(),vp.argmax(1),labels=range(len(classes)),average='macro',zero_division=0)
            history.append({'epoch':epoch,'train_loss':total/n,'validation_macro_f1':float(vf)})
            print(name,epoch,'validation macro-F1',round(float(vf),4),flush=True)
            if vf>best+1e-6:best=vf;state=copy.deepcopy(model.state_dict());stale=0;best_epoch=epoch
            else:stale+=1
            if stale>=4:break
        model.load_state_dict(state);seconds=time.perf_counter()-start
        start=time.perf_counter();prob=predict(model,name,'test');elapsed=time.perf_counter()-start
        result=score(target['test'].numpy(),prob.argmax(1),classes)
        result.update(training_seconds=seconds,inference_ms_per_output=elapsed/len(prob)*1000,best_epoch=best_epoch,
                      evaluation_unit='last flow of nonoverlapping 8-flow window' if name=='TemporalTransformer' else 'individual flow',
                      timing_scope='model and graph construction where applicable; excludes preprocessing and capture')
        results[name]=result;histories[name]=history;torch.save(state,a.artifacts/f'{name}.pt')
        metadata['models'][name]={'features':len(CONTEXT_FEATURES),'classes':len(classes)}
        pd.DataFrame({'actual':np.array(classes)[target['test'].numpy()],'predicted':np.array(classes)[prob.argmax(1)],
                      'probability':prob.max(1)}).to_csv(a.results/f'{name}_predictions.csv',index=False)
        if name=='BERTStyleEncoder':starting=copy.deepcopy(model)
        (a.results/'test_metrics.json').write_text(json.dumps(results,indent=2))
    # FedAvg is a local three-client simulation, not secure distributed deployment.
    torch.manual_seed(42);global_model=build_advanced('BERTStyleEncoder',len(CONTEXT_FEATURES),len(classes))
    clients=torch.tensor_split(torch.randperm(len(x['train'])),3);rounds=[]
    start=time.perf_counter()
    for number in range(1,4):
        updates=[local_update(global_model,x['train'][ids],y['train'][ids],epochs=2) for ids in clients]
        global_model.load_state_dict(fedavg([m.state_dict() for m in updates],[len(i) for i in clients]))
        vp=predict(global_model,'BERTStyleEncoder','validation')
        rounds.append({'round':number,'validation_macro_f1':float(f1_score(y['validation'],vp.argmax(1),labels=range(len(classes)),average='macro',zero_division=0))})
        print('FedAvg round',number,rounds[-1],flush=True)
    prob=predict(global_model,'BERTStyleEncoder','test');results['FederatedFedAvg']=score(y['test'].numpy(),prob.argmax(1),classes)
    results['FederatedFedAvg'].update(training_seconds=time.perf_counter()-start,simulation_clients=3,rounds=3,
                                     limitation='Local IID client simulation; no privacy/security or network deployment claim')
    torch.save(global_model.state_dict(),a.artifacts/'FederatedFedAvg.pt')
    metadata['models']['FederatedFedAvg']={'architecture':'BERTStyleEncoder'}
    # Delayed labels on validation-stream chunks are explicitly required for online learning.
    adaptive=copy.deepcopy(starting);drift=PageHinkley();stream=[]
    for chunk,ids in enumerate(torch.arange(len(x['validation'])).split(128)):
        adaptive.eval()
        with torch.inference_mode():
            logits=adaptive(x['validation'][ids]);loss=torch.nn.functional.cross_entropy(logits,y['validation'][ids]).item()
            accuracy=float((logits.argmax(1)==y['validation'][ids]).float().mean())
        stream.append({'chunk':chunk,'pre_update_accuracy':accuracy,'observed_loss':loss,'drift':drift.update(loss)})
        adaptive=local_update(adaptive,x['validation'][ids],y['validation'][ids],epochs=1,lr=.0001)
    prob=predict(adaptive,'BERTStyleEncoder','test');results['OnlineLearning']=score(y['test'].numpy(),prob.argmax(1),classes)
    results['OnlineLearning']['adaptation_protocol']='Predict then reveal true validation labels, update at fixed lr=.0001; evaluate frozen final model on test'
    torch.save(adaptive.state_dict(),a.artifacts/'OnlineLearning.pt');metadata['models']['OnlineLearning']={'architecture':'BERTStyleEncoder'}
    joblib.dump(joblib.load(a.data/'preprocessor.joblib'),a.artifacts/'preprocessor.joblib')
    (a.artifacts/'model_metadata.json').write_text(json.dumps(metadata,indent=2))
    (a.results/'test_metrics.json').write_text(json.dumps(results,indent=2))
    (a.results/'histories.json').write_text(json.dumps(histories,indent=2))
    (a.results/'federated_rounds.json').write_text(json.dumps(rounds,indent=2))
    pd.DataFrame(stream).to_csv(a.results/'online_prequential.csv',index=False)
    pd.DataFrame([{'model':name,**{k:m.get(k) for k in ['accuracy','macro_f1','benign_false_positive_rate','test_rows','evaluation_unit']}}
                  for name,m in results.items()]).to_csv(a.results/'model_comparison.csv',index=False)
    print('Saved advanced models, measured results and adaptation traces',flush=True)

if __name__=='__main__':main()
