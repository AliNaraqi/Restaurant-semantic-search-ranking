#!/usr/bin/env python3
"""Step 4 — Compare retrieval methods with Recall@10 and NDCG@10."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import DOCS_PARQUET, EVAL_RESULTS_PATH, LTR_MODEL_PATH
from src.evaluation.judgments import EVAL_QUERIES, build_judgment_table, judgments_by_query
from src.evaluation.metrics import mean_metric, ndcg_at_k, recall_at_k
from src.ranking.ltr import load_ltr
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.faiss_index import FaissRetriever
from src.retrieval.hybrid import HybridRetriever


def evaluate_method(
    retriever: HybridRetriever,
    method: str,
    graded_by_query: dict[str, dict[str, float]],
    k: int = 10,
) -> dict[str, float]:
    recalls = []
    ndcgs = []
    for query, graded in graded_by_query.items():
        relevant = {bid for bid, rel in graded.items() if rel >= 2}
        hits = retriever.search(query, method=method, top_k=k, use_filters=True)
        retrieved = [h.business_id for h in hits]
        recalls.append(recall_at_k(relevant, retrieved, k=k))
        ndcgs.append(ndcg_at_k(graded, retrieved, k=k))
    return {
        f"Recall@{k}": mean_metric(recalls),
        f"NDCG@{k}": mean_metric(ndcgs),
    }


def main() -> None:
    docs = pd.read_parquet(DOCS_PARQUET)
    faiss = FaissRetriever.load()
    bm25 = BM25Retriever.load()
    ltr = load_ltr(LTR_MODEL_PATH) if LTR_MODEL_PATH.exists() else None
    retriever = HybridRetriever(docs=docs, faiss=faiss, bm25=bm25, ltr_model=ltr)

    judgments = build_judgment_table(docs, EVAL_QUERIES)
    graded = judgments_by_query(judgments)

    methods = ["semantic", "bm25", "hybrid"]
    if ltr is not None:
        methods.append("ltr")

    results = {}
    print("\n=== Retrieval comparison ===\n")
    print(f"{'Method':<12} {'Recall@10':>10} {'NDCG@10':>10}")
    print("-" * 34)
    for method in methods:
        metrics = evaluate_method(retriever, method, graded, k=10)
        results[method] = metrics
        print(
            f"{method:<12} {metrics['Recall@10']:>10.4f} {metrics['NDCG@10']:>10.4f}"
        )

    EVAL_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote {EVAL_RESULTS_PATH}")


if __name__ == "__main__":
    main()
