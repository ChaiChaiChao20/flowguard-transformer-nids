"""Passive PCAP replay/live capture -> flow features -> classification -> JSONL."""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import torch
from nids.capture import FlowAggregator
from nids.inference import Predictor


def main():
    torch.set_num_threads(4)
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--pcap',type=Path);mode.add_argument('--interface');mode.add_argument('--list-interfaces',action='store_true')
    p.add_argument('--seconds',type=int,default=60);p.add_argument('--idle-timeout',type=float,default=10)
    p.add_argument('--output',type=Path,default=Path('results/live_events.jsonl'))
    p.add_argument('--artifacts',type=Path,default=Path('artifacts/extended'))
    a=p.parse_args()
    from scapy.all import PcapReader,conf,sniff
    if a.list_interfaces:print(conf.ifaces);return
    if a.seconds<=0:p.error('--seconds must be positive')
    predictor=Predictor(a.artifacts);agg=FlowAggregator(idle_timeout=a.idle_timeout)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    count=0;started=time.perf_counter()
    with a.output.open('w',encoding='utf-8') as out:
        pending=[];last_flush=time.perf_counter()
        def emit(rows,force=False):
            nonlocal count,last_flush
            pending.extend(rows)
            if not pending:return
            if not force and len(pending)<128 and time.perf_counter()-last_flush<.25:return
            ready=pending.copy();pending.clear()
            frame=pd.DataFrame(ready);prediction=predictor.predict(frame)
            for row,result in zip(ready,prediction.to_dict('records')):
                event={**row,**result,'extractor':'FlowGuard IPv4 v1',
                       'deployment_status':'experimental; extraction shift not calibrated'}
                out.write(json.dumps(event)+'\n');count+=1
            out.flush()
            last_flush=time.perf_counter()
        def callback(packet):emit(agg.consume(packet))
        if a.pcap:
            with PcapReader(str(a.pcap)) as packets:
                for packet in packets:callback(packet)
        else:
            # Bounded cycles expire idle flows and flush alerts without new packets.
            deadline=time.monotonic()+a.seconds
            while time.monotonic()<deadline:
                sniff(iface=a.interface,prn=callback,store=False,timeout=min(.25,max(.001,deadline-time.monotonic())),
                      lfilter=lambda packet:packet.haslayer('IP'))
                emit(agg.expire(time.time()),force=True)
        emit(agg.expire(float('inf'),all_flows=True),force=True)
    elapsed=time.perf_counter()-started
    summary={'flows':count,'elapsed_seconds':elapsed,'flows_per_second':count/max(elapsed,1e-9),
             'mode':'pcap replay' if a.pcap else 'live capture','output':str(a.output)}
    a.output.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
