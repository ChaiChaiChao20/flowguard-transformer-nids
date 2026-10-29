"""Explicit CICFlowMeter input contract; identifiers are excluded."""
CLASSES = ["Benign", "DoS", "DDoS", "Botnet", "Port Scan"]
LABEL_MAP = {
    "BENIGN": "Benign", "Benign": "Benign", "DoS Hulk": "DoS",
    "DoS GoldenEye": "DoS", "DoS slowloris": "DoS",
    "DoS Slowhttptest": "DoS", "DoS": "DoS", "DDoS": "DDoS",
    "Bot": "Botnet", "Botnet": "Botnet", "PortScan": "Port Scan",
    "Port Scan": "Port Scan",
}
EXTENDED_CLASSES = CLASSES + ['Brute Force', 'Infiltration']
EXTENDED_LABEL_MAP = {**LABEL_MAP, 'FTP-Patator':'Brute Force',
                      'SSH-Patator':'Brute Force', 'Infiltration':'Infiltration'}
# name, unit, explanation. Fixed before looking at validation or test scores.
FEATURE_INFO = [
    ("Flow Duration", "microseconds", "Elapsed duration of the bidirectional flow"),
    ("Total Fwd Packets", "packets", "Packets in initiating direction"),
    ("Total Backward Packets", "packets", "Packets in reverse direction"),
    ("Total Length of Fwd Packets", "bytes", "Total forward packet length"),
    ("Total Length of Bwd Packets", "bytes", "Total backward packet length"),
    ("Fwd Packet Length Max", "bytes", "Maximum forward packet length"),
    ("Fwd Packet Length Mean", "bytes", "Mean forward packet length"),
    ("Fwd Packet Length Std", "bytes", "Standard deviation of forward packet lengths"),
    ("Bwd Packet Length Max", "bytes", "Maximum backward packet length"),
    ("Bwd Packet Length Mean", "bytes", "Mean backward packet length"),
    ("Bwd Packet Length Std", "bytes", "Standard deviation of backward packet lengths"),
    ("Flow Bytes/s", "bytes/second", "Combined byte throughput"),
    ("Flow Packets/s", "packets/second", "Combined packet rate"),
    ("Flow IAT Mean", "microseconds", "Mean interval between packets"),
    ("Flow IAT Std", "microseconds", "Standard deviation of packet intervals"),
    ("Flow IAT Max", "microseconds", "Maximum packet interval"),
    ("Fwd IAT Mean", "microseconds", "Mean forward inter-arrival time"),
    ("Bwd IAT Mean", "microseconds", "Mean backward inter-arrival time"),
    ("FIN Flag Count", "count", "Packets with FIN flag"),
    ("SYN Flag Count", "count", "Packets with SYN flag"),
    ("RST Flag Count", "count", "Packets with RST flag"),
    ("PSH Flag Count", "count", "Packets with PSH flag"),
    ("ACK Flag Count", "count", "Packets with ACK flag"),
    ("Average Packet Size", "bytes", "Average size across flow packets"),
]
FEATURES = [x[0] for x in FEATURE_INFO]
