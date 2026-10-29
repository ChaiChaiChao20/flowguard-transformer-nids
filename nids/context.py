"""Deterministic network context features; raw IPs used for grouping, not IDs."""
import ipaddress,zlib
import numpy as np
import pandas as pd
from .schema import FEATURES

CONTEXT_FEATURES=FEATURES+['Source Port','Destination Port','Protocol Code','Source Private',
                          'Destination Private','Source IP Bucket','Destination IP Bucket','State Code']


def protocol_code(value):
    name=str(value).strip().upper()
    return {'TCP':1,'6':1,'UDP':2,'17':2,'ICMP':3,'1':3}.get(name,0)


def context_features(frame):
    required=['source_ip','destination_ip','source_port','destination_port','protocol']
    missing=[k for k in required if k not in frame]
    if missing:raise ValueError('Missing network context: '+', '.join(missing))
    out=frame[FEATURES].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan).copy()
    for role in ['source','destination']:
        ips=frame[role+'_ip'].map(lambda s:ipaddress.ip_address(str(s)))
        out[role.title()+' Private']=ips.map(lambda ip:int(ip.is_private))
        # Bounded categories prevent embedding table growth. Collisions are documented.
        out[role.title()+' IP Bucket']=ips.map(lambda ip:zlib.crc32(str(ip).encode())%256)
        ports=pd.to_numeric(frame[role+'_port'],errors='raise')
        if not ports.between(0,65535).all():raise ValueError('Port outside 0..65535')
        out[role.title()+' Port']=ports
    out['Protocol Code']=frame.protocol.map(protocol_code)
    out['State Code']=np.where(out['RST Flag Count']>0,2,np.where(out['FIN Flag Count']>0,1,0))
    return out[CONTEXT_FEATURES]


def categorical_features(frame):
    values=context_features(frame)
    return values[['Protocol Code','State Code']].to_numpy(dtype=np.int64)


def flow_adjacency(frame):
    src=frame.source_ip.astype(str).to_numpy();dst=frame.destination_ip.astype(str).to_numpy()
    return ((src[:,None]==src[None,:])|(src[:,None]==dst[None,:])|
            (dst[:,None]==src[None,:])|(dst[:,None]==dst[None,:])).astype('float32')


def temporal_windows(frame,values,window=8,gap_seconds=300):
    """Causal, non-overlapping windows; never span split, host, day or idle gap.

    Returns window values and final-row indices. Dropping leftovers avoids
    zero-padding artifacts. Frames must already contain a split assignment.
    """
    sequences=[];endpoints=[];members=[]
    work=frame.copy();work['_id']=np.arange(len(work));work['_day']=work.time.dt.date
    for _,group in work.groupby(['split','source_ip','_day'],sort=True):
        group=group.sort_values(['time','_id'],kind='stable')
        episodes=group.time.diff().dt.total_seconds().gt(gap_seconds).cumsum()
        for _,episode in group.groupby(episodes):
            ids=episode._id.to_numpy()
            for start in range(0,len(ids)-window+1,window):
                selected=ids[start:start+window]
                sequences.append(values[selected]);endpoints.append(int(selected[-1]));members.append(selected)
    if not sequences:raise ValueError('No complete chronological windows found')
    return np.stack(sequences),np.array(endpoints),np.stack(members)
