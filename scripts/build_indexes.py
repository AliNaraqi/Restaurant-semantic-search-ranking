#!/usr/bin/env python3
"""Step 2 — Build FAISS + BM25 indexes from processed search documents."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import DOCS_PARQUET
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.faiss_index import FaissRetriever


def main() -> None:
    if not DOCS_PARQUET.exists():
        raise SystemExit("Missing processed docs. Run: python scripts/prepare_data.py")

    docs = pd.read_parquet(DOCS_PARQUET)
    documents = docs["document"].astype(str).tolist()
    doc_ids = docs["business_id"].astype(str).tolist()

    print(f"Building FAISS index over {len(documents)} docs…")
    faiss_ret = FaissRetriever.build(documents, doc_ids)
    faiss_ret.save()
    print("  FAISS saved.")

    print("Building BM25 index…")
    bm25_ret = BM25Retriever.build(documents, doc_ids)
    bm25_ret.save()
    print("  BM25 saved.")
    print("Done.")


if __name__ == "__main__":
    main()
