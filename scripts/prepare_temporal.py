"""Prepare timestamp-preserving context and disjoint chronological windows."""
import argparse,json,sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import joblib,numpy as np,pandas as pd
from nids.schema import FEATURES,EXTENDED_CLASSES,EXTENDED_LABEL_MAP
from nids.context import CONTEXT_FEATURES,context_features,temporal_windows
from nids.preprocessing import build_preprocessor

REPO='rdpahalavan/CIC-IDS2017'
REVISION='eee96b6abc2c4bb621fd67679a4aa24bddc4be6a'
SHA256='e64f6adfbcb7f96b018cf36c731be64ef4de3353ccd7340b190590734a0dda35'

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,default=Path('data/temporal'));p.add_argument('--per-class',type=int,default=2500)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    with a.input.open('rb') as f:checksum=hashlib.file_digest(f,'sha256').hexdigest()
    if checksum!=SHA256:raise ValueError('Source hash does not match pinned mirror')
    columns=FEATURES+['source_ip','destination_ip','source_port','destination_port','protocol','Timestamp','attack_label']
    frame=pd.read_parquet(a.input,columns=columns);original=len(frame)
    frame['target']=frame.attack_label.astype(str).str.strip().map(EXTENDED_LABEL_MAP)
    unsupported=int(frame.target.isna().sum());frame=frame[frame.target.notna()].copy()
    # This mirror uses day/month/year timestamps; preserve the local capture clock.
    frame['time']=pd.to_datetime(frame.Timestamp,dayfirst=True,format='mixed',errors='coerce')
    invalid=int(frame.time.isna().sum());frame=frame[frame.time.notna()].copy()
    # This mirror retains 12-hour timestamps without AM/PM. CIC working-day
    # captures run during daytime: 01..07 are interpreted as 13..19 locally.
    # Explicit heuristic, not a claim of independently validated PCAP timing.
    corrected=frame.time.dt.hour.lt(8)
    frame.loc[corrected,'time']=frame.loc[corrected,'time']+pd.Timedelta(hours=12)
    frame['Timestamp']=frame.time.dt.strftime('%Y-%m-%d %H:%M:%S')
    print('Parsed timestamps',frame.time.min(),frame.time.max(),flush=True)
    features=frame[FEATURES].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan)
    frame['feature_hash']=pd.util.hash_pandas_object(features,index=False).to_numpy()
    conflicts=frame.groupby('feature_hash').target.nunique();bad=conflicts[conflicts>1].index
    frame=frame[~frame.feature_hash.isin(bad)].drop_duplicates('feature_hash').copy()
    # Sample before the chronological split; no label is used to form windows.
    parts=[]
    for label,part in frame.groupby('target'):
        cap=a.per_class*2 if label=='Benign' else a.per_class
        parts.append(part.sample(min(cap,len(part)),random_state=42))
    frame=pd.concat(parts).sort_values('time',kind='stable').reset_index(drop=True)
    frame['split']='train';frame['_day']=frame.time.dt.date
    # Split chronological activity episodes, formed without labels. This avoids
    # putting a short morning campaign wholly in train because a host is also
    # active later that day. Episode idle gap matches the windowing contract.
    for _,ids in frame.groupby(['source_ip','_day']).groups.items():
        group=frame.loc[list(ids)]
        episodes=group.time.diff().dt.total_seconds().gt(300).cumsum()
        for _,episode in group.groupby(episodes):
            ids=episode.index.to_numpy();n=len(ids);cut1=int(n*.7);cut2=int(n*.85)
            frame.loc[ids[cut1:cut2],'split']='validation';frame.loc[ids[cut2:],'split']='test'
    frame.drop(columns='_day',inplace=True)
    raw=context_features(frame)
    pre=build_preprocessor().fit(raw[frame.split=='train'])
    x=pre.transform(raw).astype('float32');y=frame.target.map({c:i for i,c in enumerate(EXTENDED_CLASSES)}).to_numpy(dtype='int64')
    sequences,endpoints,members=temporal_windows(frame,x)
    arrays={'class_names':np.array(EXTENDED_CLASSES)};counts={};seqcounts={}
    for split in ['train','validation','test']:
        ids=np.flatnonzero(frame.split.to_numpy()==split)
        chosen=frame.iloc[endpoints].split.to_numpy()==split
        arrays['X_'+split]=x[ids];arrays['y_'+split]=y[ids]
        arrays['sequence_'+split]=sequences[chosen];arrays['sequence_y_'+split]=y[endpoints[chosen]]
        arrays['sequence_end_'+split]=endpoints[chosen];arrays['sequence_members_'+split]=members[chosen]
        frame.iloc[ids].to_csv(a.output/f'{split}_flows.csv',index=False)
        counts[split]=frame.iloc[ids].target.value_counts().to_dict()
        seqcounts[split]=frame.iloc[endpoints[chosen]].target.value_counts().to_dict()
    np.savez_compressed(a.output/'splits.npz',**arrays);joblib.dump(pre,a.output/'preprocessor.joblib')
    frame.to_csv(a.output/'sample_manifest.csv',index=False)
    audit={'source_rows':original,'unsupported_rows':unsupported,'invalid_timestamps':invalid,
           'source_repository':REPO,'revision':REVISION,'sha256':checksum,'sample_rows':len(frame),
           'conflicting_hashes_removed':len(bad),'classes':EXTENDED_CLASSES,'features':CONTEXT_FEATURES,
           'timestamp_correction':'Working-day heuristic: hours 01..07 shifted +12h for missing AM/PM',
           'timestamp_rows_corrected':int(corrected.sum()),
           'flow_counts':counts,'sequence_endpoint_counts':seqcounts,'window':8,'max_gap_seconds':300,
           'split':'chronological 70/15/15 within each source/day activity episode (300s idle gap); nonoverlapping 8-flow windows within split',
           'limitations':['Sampled timestamps preserve chronology but omit intervening flows',
                          'AM/PM correction assumes daytime capture; original PCAP timing not independently verified',
                          'Hosts and campaigns can appear in several splits; no host-disjoint claim',
                          'Mirror not independently verified against original UNB PCAPs',
                          'Some classes may have no complete held-out windows; report support explicitly',
                          'IP buckets collide and may reflect dataset topology; assess domain shift',
                          'Connection state is inferred from FIN/RST counts, not reconstructed TCP state']}
    (a.output/'data_audit.json').write_text(json.dumps(audit,indent=2,default=str));print(json.dumps(audit,indent=2),flush=True)

if __name__=='__main__':main()
