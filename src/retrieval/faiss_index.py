"""FAISS inner-product index over L2-normalized embeddings (cosine similarity)."""

from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np

from src.config import DOC_IDS_PATH, EMBEDDINGS_PATH, FAISS_INDEX_PATH, FAISS_TOP_K
from src.retrieval.embeddings import encode_query, encode_texts


class FaissRetriever:
    def __init__(
        self,
        index: faiss.Index,
        doc_ids: list[str],
        embeddings: np.ndarray | None = None,
    ):
        self.index = index
        self.doc_ids = doc_ids
        self.embeddings = embeddings

    @classmethod
    def build(cls, documents: list[str], doc_ids: list[str]) -> "FaissRetriever":
        embeddings = encode_texts(documents, normalize=True)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)
        return cls(index=index, doc_ids=list(doc_ids), embeddings=embeddings)

    def save(
        self,
        index_path: Path = FAISS_INDEX_PATH,
        embeddings_path: Path = EMBEDDINGS_PATH,
        doc_ids_path: Path = DOC_IDS_PATH,
    ) -> None:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_path))
        if self.embeddings is not None:
            np.save(embeddings_path, self.embeddings)
        doc_ids_path.write_text(json.dumps(self.doc_ids), encoding="utf-8")

    @classmethod
    def load(
        cls,
        index_path: Path = FAISS_INDEX_PATH,
        embeddings_path: Path = EMBEDDINGS_PATH,
        doc_ids_path: Path = DOC_IDS_PATH,
    ) -> "FaissRetriever":
        index = faiss.read_index(str(index_path))
        doc_ids = json.loads(doc_ids_path.read_text(encoding="utf-8"))
        embeddings = np.load(embeddings_path) if embeddings_path.exists() else None
        return cls(index=index, doc_ids=doc_ids, embeddings=embeddings)

    def search(self, query: str, top_k: int = FAISS_TOP_K) -> list[tuple[str, float]]:
        q = encode_query(query).reshape(1, -1)
        scores, idxs = self.index.search(q, top_k)
        results: list[tuple[str, float]] = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx < 0:
                continue
            results.append((self.doc_ids[int(idx)], float(score)))
        return results
