"""Deterministic file output for synthetic, SI-valued panel calculations."""
from pathlib import Path
import csv
import hashlib
import json
import platform

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams.update({"svg.hashsalt": "newton-tesla-lab-v1", "font.size": 10})
import matplotlib.pyplot as plt
import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n")

def write_csv(path, columns, rows):
    with Path(path).open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerows(rows)

def save_figure(path, fig):
    fig.savefig(path, format="svg", metadata={"Date": None, "Creator": "NumPy/SciPy/Matplotlib synthetic calculation"}, bbox_inches="tight")
    plt.close(fig)

def write_manifest(round_dir, contract_path):
    """Bind byte-level artifacts, producer and contract after all outputs exist."""
    round_dir = Path(round_dir)
    paths = sorted(p for p in round_dir.rglob("*") if p.is_file() and p.name != "manifest.json" and "__pycache__" not in p.parts)
    manifest = {
        "schemaVersion": 1,
        "kind": "synthetic-producer-artifacts",
        "round": round_dir.name,
        "contract": {"path": str(Path(contract_path).relative_to(ROOT)), "sha256": sha256(contract_path)},
        "dependencies": [{"path": "scripts/numerics.py", "sha256": sha256(__file__)}, {"path": "requirements.txt", "sha256": sha256(ROOT / "requirements.txt")}],
        "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "matplotlib": matplotlib.__version__},
        "files": [{"path": str(p.relative_to(ROOT)), "sha256": sha256(p), "bytes": p.stat().st_size} for p in paths],
    }
    write_json(round_dir / "manifest.json", manifest)
    return manifest
