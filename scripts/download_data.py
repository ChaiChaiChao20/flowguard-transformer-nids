"""Download pinned public CIC-IDS2017 CSV mirror; record hashes and provenance."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import requests

REPO = "c01dsnap/CIC-IDS2017"
REVISION = "4e9edfa727f800b6f595bc2ee7420527156562b2"
FILES = ["Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
         "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
         "Friday-WorkingHours-Morning.pcap_ISCX.csv",
         "Wednesday-workingHours.pcap_ISCX.csv"]
SIZES = dict(zip(FILES, [77123859, 76906168, 58316725, 225166395]))
EXTRA_FILES=['Tuesday-WorkingHours.pcap_ISCX.csv','Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv']
SIZES.update(dict(zip(EXTRA_FILES,[135078995,83102436])))


def download_one(args):
    filename, root = args
    url = f"https://huggingface.co/datasets/{REPO}/resolve/{REVISION}/{filename}?download=true"
    target = root / filename
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists() or target.stat().st_size != SIZES[filename]:
        partial = target.with_suffix(".part")
        print(f"Downloading {filename}", flush=True)
        failures = 0
        while not partial.exists() or partial.stat().st_size < SIZES[filename]:
            offset = partial.stat().st_size if partial.exists() else 0
            end = min(offset + 16*1024*1024 - 1, SIZES[filename]-1)
            try:
                with requests.get(url, headers={"Range": f"bytes={offset}-{end}"}, timeout=(30, 60), stream=True) as response:
                    response.raise_for_status()
                    if "text/html" in response.headers.get("Content-Type", ""):
                        raise RuntimeError("Expected CSV data, received an HTML response.")
                    if response.status_code == 206 and not response.headers.get("Content-Range", "").startswith(f"bytes {offset}-"):
                        raise RuntimeError("Unexpected download range.")
                    mode = "ab" if response.status_code == 206 and offset else "wb"
                    with partial.open(mode) as f:
                        for block in response.iter_content(1024*1024):
                            f.write(block)
                failures = 0
                print(f"  {filename}: {partial.stat().st_size:,}/{SIZES[filename]:,}", flush=True)
            except requests.RequestException as error:
                failures += 1
                if failures >= 5:
                    raise
                print(f"Retrying resumable download: {type(error).__name__}", flush=True)
                time.sleep(min(failures*2, 10))
        if partial.stat().st_size != SIZES[filename]:
            raise RuntimeError("Downloaded file size does not match pinned repository metadata.")
        partial.replace(target)
    checksum = hashlib.sha256()
    with target.open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""):
            checksum.update(block)
    print(f"Ready {filename}: {target.stat().st_size:,} bytes", flush=True)
    return {"file": filename, "url": url, "bytes": target.stat().st_size,
            "sha256": checksum.hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    parser.add_argument('--extended',action='store_true',help='Also download brute-force and infiltration source days')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(download_one, [(f, args.output) for f in FILES+(EXTRA_FILES if args.extended else [])]))
    manifest = {"dataset": "CIC-IDS2017 public mirror (not independently verified against original)",
                "official_source": "https://www.unb.ca/cic/datasets/ids-2017.html",
                "mirror_repository": REPO, "mirror_revision": REVISION,
                "downloaded_at_utc": datetime.now(timezone.utc).isoformat(), "files": records,
                "citation": "Sharafaldin, Lashkari and Ghorbani. Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization. ICISSP 2018."}
    (args.output / "provenance.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
