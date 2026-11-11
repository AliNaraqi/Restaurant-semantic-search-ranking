"""Feature engineering for learning-to-rank."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.llm.query_parser import ParsedQuery
from src.retrieval.hybrid import RankedHit

FEATURE_NAMES = [
    "semantic_score",
    "bm25_score",
    "hybrid_score",
    "stars",
    "log_review_count",
    "price_range",
    "vegetarian_match",
    "quiet_match",
    "romantic_match",
    "cuisine_match",
    "city_match",
    "noise_quiet",
    "noise_loud",
]


def _cuisine_overlap(hit_cuisines: list, query_cuisines: list[str]) -> float:
    if not query_cuisines:
        return 0.0
    hit = {c.lower() for c in (hit_cuisines or [])}
    q = {c.lower() for c in query_cuisines}
    if not hit:
        return 0.0
    return len(hit & q) / len(q)


def hit_to_features(hit: RankedHit, parsed: ParsedQuery) -> dict[str, float]:
    meta = hit.metadata or {}
    noise = str(meta.get("noise_level") or "")
    return {
        "semantic_score": float(hit.semantic_score or 0.0),
        "bm25_score": float(hit.bm25_score or 0.0),
        "hybrid_score": float(hit.hybrid_score or hit.score or 0.0),
        "stars": float(meta.get("stars") or 0.0),
        "log_review_count": float(np.log1p(meta.get("review_count") or 0)),
        "price_range": float(meta.get("price_range") or 0),
        "vegetarian_match": float(
            1.0 if parsed.vegetarian and meta.get("vegetarian_friendly") else 0.0
        ),
        "quiet_match": float(1.0 if parsed.quiet and meta.get("quiet") else 0.0),
        "romantic_match": float(1.0 if parsed.romantic and meta.get("romantic") else 0.0),
        "cuisine_match": _cuisine_overlap(meta.get("cuisines") or [], parsed.cuisines),
        "city_match": float(
            1.0
            if parsed.city and str(meta.get("city", "")).lower() == parsed.city.lower()
            else 0.0
        ),
        "noise_quiet": float(1.0 if noise == "quiet" else 0.0),
        "noise_loud": float(1.0 if noise in {"loud", "very_loud"} else 0.0),
    }


def build_feature_matrix(
    hits: list[RankedHit], parsed: ParsedQuery
) -> np.ndarray:
    rows = [hit_to_features(h, parsed) for h in hits]
    df = pd.DataFrame(rows, columns=FEATURE_NAMES)
    return df.to_numpy(dtype=np.float32)


def features_dataframe(
    hits: list[RankedHit], parsed: ParsedQuery
) -> pd.DataFrame:
    rows = [hit_to_features(h, parsed) for h in hits]
    df = pd.DataFrame(rows, columns=FEATURE_NAMES)
    df.insert(0, "business_id", [h.business_id for h in hits])
    return df
