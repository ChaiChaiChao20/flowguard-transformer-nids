"""Bounded passive IPv4 TCP/UDP flow aggregation for PCAP and live capture.

The extractor has explicit semantics; CICFlowMeter equivalence is NOT assumed.
No payload is retained and no traffic is generated or blocked.
"""
from dataclasses import dataclass,field
import numpy as np


@dataclass
class Flow:
    source: str
    destination: str
    source_port: int
    destination_port: int
    protocol: int
    start: float
    end: float
    times: list=field(default_factory=list)
    forward_times: list=field(default_factory=list)
    backward_times: list=field(default_factory=list)
    forward_sizes: list=field(default_factory=list)
    backward_sizes: list=field(default_factory=list)
    flags: dict=field(default_factory=lambda:{f:0 for f in ['FIN','SYN','RST','PSH','ACK']})

    def add(self,time,size,forward,flags):
        self.end=max(self.end,time);self.times.append(time)
        (self.forward_times if forward else self.backward_times).append(time)
        (self.forward_sizes if forward else self.backward_sizes).append(size)
        for name,bit in [('FIN',1),('SYN',2),('RST',4),('PSH',8),('ACK',16)]:
            self.flags[name]+=int(bool(flags&bit))

    def features(self):
        def summary(values):
            return (float(np.max(values)),float(np.mean(values)),float(np.std(values))) if len(values) else (0.,0.,0.)
        def intervals(times):return np.diff(sorted(times))*1e6
        fmax,fmean,fstd=summary(self.forward_sizes);bmax,bmean,bstd=summary(self.backward_sizes)
        imax,imean,istd=summary(intervals(self.times))
        duration=(self.end-self.start)*1e6;seconds=max(duration/1e6,1e-6)
        return {'Flow Duration':duration,'Total Fwd Packets':len(self.forward_sizes),
          'Total Backward Packets':len(self.backward_sizes),'Total Length of Fwd Packets':sum(self.forward_sizes),
          'Total Length of Bwd Packets':sum(self.backward_sizes),'Fwd Packet Length Max':fmax,
          'Fwd Packet Length Mean':fmean,'Fwd Packet Length Std':fstd,'Bwd Packet Length Max':bmax,
          'Bwd Packet Length Mean':bmean,'Bwd Packet Length Std':bstd,
          'Flow Bytes/s':sum(self.forward_sizes+self.backward_sizes)/seconds,
          'Flow Packets/s':len(self.times)/seconds,'Flow IAT Mean':imean,'Flow IAT Std':istd,
          'Flow IAT Max':imax,'Fwd IAT Mean':summary(intervals(self.forward_times))[1],
          'Bwd IAT Mean':summary(intervals(self.backward_times))[1],
          **{name+' Flag Count':value for name,value in self.flags.items()},
          'Average Packet Size':float(np.mean(self.forward_sizes+self.backward_sizes)),
          'Source IP':self.source,'Destination IP':self.destination,'Source Port':self.source_port,
          'Destination Port':self.destination_port,'Protocol':self.protocol,'Timestamp':self.start,
          'Connection State':'RESET' if self.flags['RST'] else 'CLOSED' if self.flags['FIN'] else 'OPEN'}


class FlowAggregator:
    def __init__(self,idle_timeout=10,active_timeout=120,max_flows=10000,max_packets=4096):
        if min(idle_timeout,active_timeout,max_flows,max_packets)<=0:raise ValueError('Positive limits required')
        self.idle_timeout=idle_timeout;self.active_timeout=active_timeout
        self.max_flows=max_flows;self.max_packets=max_packets;self.flows={};self.last_time=None

    def expire(self,now,all_flows=False):
        ready=[]
        for key,flow in list(self.flows.items()):
            if all_flows or now-flow.end>=self.idle_timeout or now-flow.start>=self.active_timeout:
                ready.append(flow.features());del self.flows[key]
        return ready

    def consume(self,packet):
        from scapy.layers.inet import IP,TCP,UDP
        if IP not in packet or (TCP not in packet and UDP not in packet):return []
        ip=packet[IP];transport=packet[TCP] if TCP in packet else packet[UDP]
        now=float(packet.time)
        if self.last_time is not None and now<self.last_time:
            raise ValueError('Capture must be in nondecreasing timestamp order')
        self.last_time=now;ready=self.expire(now)
        key=(str(ip.src),str(ip.dst),int(transport.sport),int(transport.dport),int(ip.proto))
        reverse=(key[1],key[0],key[3],key[2],key[4])
        forward=True
        if reverse in self.flows:key=reverse;forward=False
        if key not in self.flows:
            if len(self.flows)>=self.max_flows:
                oldest=min(self.flows,key=lambda k:self.flows[k].end)
                ready.append(self.flows.pop(oldest).features())
            self.flows[key]=Flow(*key,now,now)
        flow=self.flows[key]
        flow.add(now,len(bytes(ip)),forward,int(transport.flags) if TCP in packet else 0)
        if len(flow.times)>=self.max_packets or (TCP in packet and int(transport.flags)&5):
            ready.append(self.flows.pop(key).features())
        return ready
