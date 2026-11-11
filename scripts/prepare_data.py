#!/usr/bin/env python3
"""Step 1 — Generate sample data (if needed) and preprocess into parquet."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import BUSINESS_FILE, SAMPLE_DIR
from src.data.preprocess import prepare_all


def main() -> None:
    sample_biz = SAMPLE_DIR / "businesses.jsonl"
    if not BUSINESS_FILE.exists() or BUSINESS_FILE == sample_biz:
        print("Generating / refreshing sample Yelp-schema data…")
        runpy.run_path(str(ROOT / "scripts" / "generate_sample_data.py"), run_name="__main__")
    else:
        print(f"Using Yelp dump at {BUSINESS_FILE}")

    prepare_all(save=True)


if __name__ == "__main__":
    main()
