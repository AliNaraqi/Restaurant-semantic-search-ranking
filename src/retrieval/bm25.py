"""BM25 lexical retrieval over restaurant documents."""

from __future__ import annotations

import pickle
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

from src.config import BM25_PATH, BM25_TOP_K

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class BM25Retriever:
    def __init__(self, bm25: BM25Okapi, doc_ids: list[str], corpus_tokens: list[list[str]]):
        self.bm25 = bm25
        self.doc_ids = doc_ids
        self.corpus_tokens = corpus_tokens

    @classmethod
    def build(cls, documents: list[str], doc_ids: list[str]) -> "BM25Retriever":
        corpus_tokens = [tokenize(doc) for doc in documents]
        bm25 = BM25Okapi(corpus_tokens)
        return cls(bm25=bm25, doc_ids=list(doc_ids), corpus_tokens=corpus_tokens)

    def save(self, path: Path = BM25_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            pickle.dump(
                {
                    "doc_ids": self.doc_ids,
                    "corpus_tokens": self.corpus_tokens,
                },
                f,
            )

    @classmethod
    def load(cls, path: Path = BM25_PATH) -> "BM25Retriever":
        with path.open("rb") as f:
            payload = pickle.load(f)
        bm25 = BM25Okapi(payload["corpus_tokens"])
        return cls(
            bm25=bm25,
            doc_ids=payload["doc_ids"],
            corpus_tokens=payload["corpus_tokens"],
        )

    def search(self, query: str, top_k: int = BM25_TOP_K) -> list[tuple[str, float]]:
        tokens = tokenize(query)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        ranked = sorted(
            enumerate(scores), key=lambda x: float(x[1]), reverse=True
        )[:top_k]
        return [(self.doc_ids[i], float(s)) for i, s in ranked if s > 0]
