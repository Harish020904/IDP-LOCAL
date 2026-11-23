"""Integrity and provenance verification for IoT-23 dataset."""
import hashlib
from pathlib import Path
from typing import Dict, Tuple

DATASET_A_SLUG = "harishragavender0209/iot-23-raw"
DOI = "10.5281/zenodo.4743746"

# Canonical raw capture file sizes (in bytes) confirmed from Kaggle Dataset A
RAW_FILE_SIZES: Dict[str, int] = {
    "10.labeled": 1340179107,
    "11.labeled": 3019311,
    "12.labeled": 7867920121,
    "13.labeled": 428943,
    "14.labeled": 419604,
    "15.labeled": 8139370158,
    "2.labeled": 3070319722,
    "3.labeled": 853630635,
    "4.labeled": 531738215,
    "5.labeled": 31179,
    "6.labeled": 9363261631,
    "7.labeled": 585829,
    "8.labeled": 10885361439,
    "9.labeled": 1787852355,
    "benign-honeypot2.labeled": 182147,
    "benign-honeypot3.labeled": 18024,
    "benign.labeled": 61653,
    "conn.log.labeled": 467559811,
}

TOTAL_RAW_BYTES = sum(RAW_FILE_SIZES.values())
TOTAL_RAW_FILES = len(RAW_FILE_SIZES)

def verify_file_size(filename: str, actual_size: int) -> bool:
    """Check if actual file size matches canonical record."""
    expected = RAW_FILE_SIZES.get(filename)
    if expected is None:
        raise ValueError(f"Unknown raw capture file: {filename}")
    return expected == actual_size

def compute_stream_sha256(filepath: Path, chunk_size: int = 65536) -> str:
    """Compute SHA-256 in memory-efficient stream chunks."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()
