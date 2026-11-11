"""Ranking metrics: Recall@K and NDCG@K."""

from __future__ import annotations

import math
from typing import Iterable, Sequence


def recall_at_k(
    relevant: set[str],
    retrieved: Sequence[str],
    k: int = 10,
) -> float:
    if not relevant:
        return 0.0
    top = list(retrieved)[:k]
    hits = sum(1 for doc_id in top if doc_id in relevant)
    return hits / len(relevant)


def dcg_at_k(relevances: Sequence[float], k: int = 10) -> float:
    score = 0.0
    for i, rel in enumerate(list(relevances)[:k]):
        score += (2**rel - 1) / math.log2(i + 2)
    return score


def ndcg_at_k(
    graded: dict[str, float],
    retrieved: Sequence[str],
    k: int = 10,
) -> float:
    if not graded:
        return 0.0
    rels = [float(graded.get(doc_id, 0.0)) for doc_id in list(retrieved)[:k]]
    ideal = sorted(graded.values(), reverse=True)
    ideal_dcg = dcg_at_k(ideal, k)
    if ideal_dcg == 0:
        return 0.0
    return dcg_at_k(rels, k) / ideal_dcg


def mean_metric(
    per_query: Iterable[float],
) -> float:
    vals = list(per_query)
    return sum(vals) / len(vals) if vals else 0.0
