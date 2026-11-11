"""Sentence-Transformer embeddings for restaurant documents and queries."""

from __future__ import annotations

from functools import lru_cache
from typing import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_encoder(model_name: str | None = None) -> SentenceTransformer:
    name = model_name or EMBEDDING_MODEL
    return SentenceTransformer(name)


def encode_texts(
    texts: Sequence[str],
    model_name: str | None = None,
    batch_size: int = 64,
    normalize: bool = True,
    show_progress: bool = True,
) -> np.ndarray:
    model = get_encoder(model_name)
    embeddings = model.encode(
        list(texts),
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
        normalize_embeddings=normalize,
    )
    return np.asarray(embeddings, dtype=np.float32)


def encode_query(query: str, model_name: str | None = None) -> np.ndarray:
    return encode_texts([query], model_name=model_name, show_progress=False)[0]
