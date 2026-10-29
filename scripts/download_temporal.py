"""Pinned timestamp-preserving CIC-IDS2017 mirror (369.8 MB)."""
import argparse,json
from pathlib import Path
import download_data as d
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path('data/raw'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
d.REPO='rdpahalavan/CIC-IDS2017';d.REVISION='eee96b6abc2c4bb621fd67679a4aa24bddc4be6a'
name='Network-Flows/CICIDS_Flow.parquet';d.SIZES[name]=369814810
record=d.download_one((name,a.output))
expected='e64f6adfbcb7f96b018cf36c731be64ef4de3353ccd7340b190590734a0dda35'
if record['sha256']!=expected:raise ValueError('Pinned mirror SHA-256 mismatch')
record.update(repository=d.REPO,revision=d.REVISION,official_source='https://www.unb.ca/cic/datasets/ids-2017.html')
(a.output/'temporal_provenance.json').write_text(json.dumps(record,indent=2))
