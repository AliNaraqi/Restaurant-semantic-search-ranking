"""Hybrid retrieval: FAISS semantic + BM25 lexical + metadata filters + optional LTR."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from src.config import BM25_WEIGHT, FINAL_TOP_K, HYBRID_TOP_K, SEMANTIC_WEIGHT
from src.data.utils import as_list
from src.llm.query_parser import ParsedQuery, parse_query
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.faiss_index import FaissRetriever
from src.retrieval.filters import apply_metadata_filters


def _normalize_scores(pairs: list[tuple[str, float]]) -> dict[str, float]:
    if not pairs:
        return {}
    vals = np.array([s for _, s in pairs], dtype=np.float64)
    lo, hi = float(vals.min()), float(vals.max())
    if hi - lo < 1e-9:
        return {doc_id: 1.0 for doc_id, _ in pairs}
    return {doc_id: float((s - lo) / (hi - lo)) for doc_id, s in pairs}


@dataclass
class RankedHit:
    business_id: str
    score: float
    semantic_score: float = 0.0
    bm25_score: float = 0.0
    hybrid_score: float = 0.0
    ltr_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class HybridRetriever:
    def __init__(
        self,
        docs: pd.DataFrame,
        faiss: FaissRetriever,
        bm25: BM25Retriever,
        ltr_model: Any | None = None,
        semantic_weight: float = SEMANTIC_WEIGHT,
        bm25_weight: float = BM25_WEIGHT,
    ):
        self.docs = docs.set_index("business_id", drop=False)
        self.faiss = faiss
        self.bm25 = bm25
        self.ltr_model = ltr_model
        self.semantic_weight = semantic_weight
        self.bm25_weight = bm25_weight

    def _meta(self, business_id: str) -> dict[str, Any]:
        if business_id not in self.docs.index:
            return {"business_id": business_id}
        row = self.docs.loc[business_id]
        if isinstance(row, pd.DataFrame):
            row = row.iloc[0]
        return {
            "business_id": business_id,
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
        }

    def search_semantic(self, query: str, top_k: int = HYBRID_TOP_K) -> list[RankedHit]:
        hits = self.faiss.search(query, top_k=top_k)
        return [
            RankedHit(business_id=bid, score=s, semantic_score=s, metadata=self._meta(bid))
            for bid, s in hits
        ]

    def search_bm25(self, query: str, top_k: int = HYBRID_TOP_K) -> list[RankedHit]:
        hits = self.bm25.search(query, top_k=top_k)
        return [
            RankedHit(business_id=bid, score=s, bm25_score=s, metadata=self._meta(bid))
            for bid, s in hits
        ]

    def search_hybrid(
        self,
        query: str,
        parsed: ParsedQuery | None = None,
        top_k: int = HYBRID_TOP_K,
        use_filters: bool = True,
    ) -> list[RankedHit]:
        parsed = parsed or parse_query(query)
        search_text = parsed.search_text or query

        sem = _normalize_scores(self.faiss.search(search_text, top_k=top_k * 2))
        lex = _normalize_scores(self.bm25.search(search_text, top_k=top_k * 2))
        all_ids = set(sem) | set(lex)

        allowed: set[str] | None = None
        if use_filters:
            filtered = apply_metadata_filters(self.docs.reset_index(drop=True), parsed, soft=True)
            allowed = set(filtered["business_id"].astype(str))

        fused: list[RankedHit] = []
        for bid in all_ids:
            if allowed is not None and bid not in allowed:
                continue
            s = sem.get(bid, 0.0)
            b = lex.get(bid, 0.0)
            score = self.semantic_weight * s + self.bm25_weight * b
            # Soft boosts from metadata alignment
            meta = self._meta(bid)
            if parsed.quiet and meta.get("quiet"):
                score += 0.05
            if parsed.romantic and meta.get("romantic"):
                score += 0.05
            if parsed.vegetarian and meta.get("vegetarian_friendly"):
                score += 0.05
            fused.append(
                RankedHit(
                    business_id=bid,
                    score=score,
                    semantic_score=s,
                    bm25_score=b,
                    hybrid_score=score,
                    metadata=meta,
                )
            )

        fused.sort(key=lambda h: h.score, reverse=True)
        return fused[:top_k]

    def search(
        self,
        query: str,
        method: str = "ltr",
        top_k: int = FINAL_TOP_K,
        use_filters: bool = True,
        parsed: ParsedQuery | None = None,
    ) -> list[RankedHit]:
        """method: semantic | bm25 | hybrid | ltr"""
        parsed = parsed or parse_query(query)
        method = method.lower()

        if method == "semantic":
            hits = self.search_semantic(parsed.search_text or query, top_k=max(top_k, HYBRID_TOP_K))
        elif method == "bm25":
            hits = self.search_bm25(parsed.search_text or query, top_k=max(top_k, HYBRID_TOP_K))
        else:
            hits = self.search_hybrid(
                query, parsed=parsed, top_k=max(top_k, HYBRID_TOP_K), use_filters=use_filters
            )

        if method == "ltr" and self.ltr_model is not None:
            from src.ranking.features import build_feature_matrix
            from src.ranking.ltr import predict_ltr

            feats = build_feature_matrix(hits, parsed)
            scores = predict_ltr(self.ltr_model, feats)
            for hit, s in zip(hits, scores):
                hit.ltr_score = float(s)
                hit.score = float(s)
            hits.sort(key=lambda h: h.score, reverse=True)

        return hits[:top_k]
