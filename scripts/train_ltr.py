#!/usr/bin/env python3
"""Step 3 — Train LightGBM LambdaRank on hybrid candidates + graded labels."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import DOCS_PARQUET
from src.data.utils import as_list
from src.evaluation.judgments import EVAL_QUERIES, build_judgment_table, grade_restaurant
from src.llm.query_parser import parse_query
from src.ranking.features import FEATURE_NAMES, hit_to_features
from src.ranking.ltr import save_ltr, train_ltr
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.faiss_index import FaissRetriever
from src.retrieval.hybrid import HybridRetriever, RankedHit


def main() -> None:
    docs = pd.read_parquet(DOCS_PARQUET)
    faiss = FaissRetriever.load()
    bm25 = BM25Retriever.load()
    retriever = HybridRetriever(docs=docs, faiss=faiss, bm25=bm25, ltr_model=None)

    judgments = build_judgment_table(docs, EVAL_QUERIES)
    print(f"Judgment pairs: {len(judgments)}")

    X_rows: list[list[float]] = []
    y_rows: list[int] = []
    group: list[int] = []

    docs_indexed = docs.set_index("business_id", drop=False)

    for query in EVAL_QUERIES:
        parsed = parse_query(query)
        hits = retriever.search_hybrid(query, parsed=parsed, top_k=30, use_filters=True)
        # Ensure some labeled negatives/positives are present
        labeled_ids = set(
            judgments.loc[judgments["query"] == query, "business_id"].astype(str)
        )
        existing = {h.business_id for h in hits}
        for bid in list(labeled_ids - existing)[:10]:
            row = docs_indexed.loc[bid]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            hits.append(
                RankedHit(
                    business_id=bid,
                    score=0.0,
                    metadata={
                        "business_id": bid,
                        "name": row.get("name"),
                        "city": row.get("city"),
                        "stars": float(row.get("stars") or 0),
                        "review_count": int(row.get("review_count") or 0),
                        "categories": row.get("categories"),
                        "price_range": int(row.get("price_range") or 0),
                        "noise_level": row.get("noise_level"),
                        "vegetarian_friendly": bool(row.get("vegetarian_friendly")),
                        "quiet": bool(row.get("quiet")),
                        "romantic": bool(row.get("romantic")),
                        "cuisines": as_list(row.get("cuisines")),
                    },
                )
            )

        n = 0
        for hit in hits:
            row = docs_indexed.loc[hit.business_id]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            rel = grade_restaurant(row, parsed)
            feats = hit_to_features(hit, parsed)
            X_rows.append([feats[name] for name in FEATURE_NAMES])
            y_rows.append(rel)
            n += 1
        if n:
            group.append(n)

    X = np.asarray(X_rows, dtype=np.float32)
    y = np.asarray(y_rows, dtype=np.float32)
    print(f"Training matrix: X={X.shape}, groups={len(group)}")

    model = train_ltr(X, y, group)
    save_ltr(model)
    print("Saved LTR model.")
    importance = sorted(
        zip(FEATURE_NAMES, model.feature_importance("gain")),
        key=lambda t: t[1],
        reverse=True,
    )
    print("Top features by gain:")
    for name, gain in importance[:8]:
        print(f"  {name}: {gain:.1f}")


if __name__ == "__main__":
    main()
