"""Small synthetic PCAP for testing the pipeline, never model accuracy."""
from pathlib import Path
from scapy.all import Ether,IP,TCP,UDP,Raw,wrpcap
packets=[]
for i in range(12):
    source=f'10.0.0.{i+1}';destination='10.0.1.1'
    for j in range(4):
        if i%2==0:
            packet=Ether(src='02:00:00:00:00:01',dst='02:00:00:00:00:02')/IP(src=source,dst=destination)/TCP(sport=4000+i,dport=80,flags='F' if j==3 else 'A')/Raw(b'x'*(20+j))
        else:
            packet=Ether(src='02:00:00:00:00:01',dst='02:00:00:00:00:02')/IP(src=source,dst=destination)/UDP(sport=4000+i,dport=53)/Raw(b'x'*(20+j))
        packet.time=1700000000+i*2+j*.1;packets.append(packet)
root=Path(__file__).resolve().parents[1]/'data/samples';root.mkdir(exist_ok=True)
wrpcap(str(root/'synthetic_pipeline_demo.pcap'),packets)
print('Wrote 48 synthetic packets; no ground-truth attack labels')
