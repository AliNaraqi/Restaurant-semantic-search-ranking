"""FastAPI web app + API for FoodBot restaurant search & chat."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.chat import build_reply
from src.api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ParsedQueryOut,
    RestaurantResult,
    SearchRequest,
    SearchResponse,
)
from src.config import DOCS_PARQUET, LTR_MODEL_PATH, PROJECT_ROOT
from src.data.utils import as_list
from src.llm.query_parser import parse_query
from src.ranking.ltr import load_ltr
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.faiss_index import FaissRetriever
from src.retrieval.hybrid import HybridRetriever, RankedHit

WEB_DIR = PROJECT_ROOT / "web"
_state: dict[str, Any] = {}


def _load_engine() -> HybridRetriever:
    if not DOCS_PARQUET.exists():
        raise RuntimeError(
            "Processed data missing. Run: python scripts/prepare_data.py && "
            "python scripts/build_indexes.py && python scripts/train_ltr.py"
        )
    docs = pd.read_parquet(DOCS_PARQUET)
    faiss = FaissRetriever.load()
    bm25 = BM25Retriever.load()
    ltr = load_ltr(LTR_MODEL_PATH) if LTR_MODEL_PATH.exists() else None
    return HybridRetriever(docs=docs, faiss=faiss, bm25=bm25, ltr_model=ltr)


def _hit_to_result(h: RankedHit, score_0_5: float) -> RestaurantResult:
    meta = h.metadata or {}
    return RestaurantResult(
        business_id=h.business_id,
        name=meta.get("name"),
        city=meta.get("city"),
        stars=meta.get("stars"),
        review_count=meta.get("review_count"),
        categories=meta.get("categories"),
        price_range=meta.get("price_range"),
        noise_level=meta.get("noise_level"),
        vegetarian_friendly=meta.get("vegetarian_friendly"),
        quiet=meta.get("quiet"),
        romantic=meta.get("romantic"),
        cuisines=as_list(meta.get("cuisines")),
        score=score_0_5,
        semantic_score=h.semantic_score,
        bm25_score=h.bm25_score,
        hybrid_score=h.hybrid_score,
        ltr_score=h.ltr_score,
    )


def _scores_to_five(hits: list[RankedHit]) -> list[RestaurantResult]:
    """Blend ranking score with Yelp stars into a 0–5 display score."""
    if not hits:
        return []
    vals = [float(h.score or 0) for h in hits]
    lo, hi = min(vals), max(vals)
    out: list[RestaurantResult] = []
    for h, raw in zip(hits, vals):
        yelp = float((h.metadata or {}).get("stars") or 0)
        yelp = max(0.0, min(5.0, yelp))
        if hi - lo < 1e-9:
            match5 = yelp or 3.5
        else:
            match5 = 3.0 + 2.0 * ((raw - lo) / (hi - lo))
        blended = round(max(0.0, min(5.0, 0.5 * match5 + 0.5 * (yelp or match5))), 1)
        out.append(_hit_to_result(h, blended))
    return out


def _parsed_out(parsed) -> ParsedQueryOut:
    return ParsedQueryOut(
        search_text=parsed.search_text,
        cuisines=parsed.cuisines,
        vegetarian=parsed.vegetarian,
        vegan=parsed.vegan,
        quiet=parsed.quiet,
        romantic=parsed.romantic,
        price_max=parsed.price_max,
        city=parsed.city,
        occasion=parsed.occasion,
    )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        _state["retriever"] = _load_engine()
        _state["load_error"] = None
    except Exception as exc:  # noqa: BLE001
        _state["retriever"] = None
        _state["load_error"] = str(exc)
        print(f"[startup] Engine not loaded: {exc}")
    yield
    _state.clear()


app = FastAPI(
    title="FoodBot — AI Restaurant Search",
    description=(
        "Natural-language restaurant discovery using semantic embeddings (FAISS), "
        "BM25, metadata filters, and LightGBM learning-to-rank — plus a chat assistant."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


@app.get("/")
def home() -> FileResponse:
    index = WEB_DIR / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Web UI missing (web/index.html)")
    return FileResponse(index)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    retriever: HybridRetriever | None = _state.get("retriever")
    if retriever is None:
        raise HTTPException(
            status_code=503,
            detail=_state.get("load_error") or "Engine not loaded",
        )
    return HealthResponse(
        status="ok",
        restaurants_indexed=len(retriever.docs),
        ltr_loaded=retriever.ltr_model is not None,
        extras={
            "embedding_backend": "sentence-transformers + FAISS",
            "lexical_backend": "BM25Okapi",
            "ranker": "LightGBM LambdaRank" if retriever.ltr_model else "hybrid only",
            "chat": True,
        },
    )


def _apply_ui_filters(parsed, req: SearchRequest):
    """Merge location / vibe / price controls into the parsed query."""
    data = parsed.model_dump()
    if req.city:
        data["city"] = req.city
    if req.price_max is not None:
        data["price_max"] = req.price_max
    vibe = (req.vibe or "any").lower()
    if vibe == "quiet":
        data["quiet"] = True
    elif vibe == "romantic":
        data["romantic"] = True
        data["occasion"] = data.get("occasion") or "date"
    elif vibe == "vegetarian":
        data["vegetarian"] = True
    return parsed.model_validate(data)


def _sort_results(results: list[RestaurantResult], sort_by: str) -> list[RestaurantResult]:
    if sort_by == "rating":
        return sorted(results, key=lambda r: (r.stars or 0, r.score), reverse=True)
    if sort_by == "value":
        # Prefer lower price, then higher match score
        return sorted(
            results,
            key=lambda r: (
                r.price_range if r.price_range and r.price_range > 0 else 99,
                -(r.score or 0),
            ),
        )
    if sort_by == "quiet":
        return sorted(
            results,
            key=lambda r: (1 if r.quiet else 0, r.score or 0),
            reverse=True,
        )
    # Best match (LTR / hybrid score already ordered)
    return results


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest) -> SearchResponse:
    retriever: HybridRetriever | None = _state.get("retriever")
    if retriever is None:
        raise HTTPException(
            status_code=503,
            detail=_state.get("load_error") or "Engine not loaded",
        )

    method = req.method
    if method == "ltr" and retriever.ltr_model is None:
        method = "hybrid"

    parsed = _apply_ui_filters(parse_query(req.query), req)
    # Pull a wider candidate set when re-sorting by rating/value/quiet
    fetch_k = req.top_k if req.sort_by == "match" else max(req.top_k, 20)
    hits = retriever.search(
        req.query,
        method=method,
        top_k=fetch_k,
        use_filters=req.use_filters,
        parsed=parsed,
    )
    results = _sort_results(_scores_to_five(hits), req.sort_by)[: req.top_k]

    return SearchResponse(
        query=req.query,
        method=method,
        parsed=_parsed_out(parsed),
        results=results,
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    retriever: HybridRetriever | None = _state.get("retriever")
    if retriever is None:
        raise HTTPException(
            status_code=503,
            detail=_state.get("load_error") or "Engine not loaded",
        )

    method = req.method
    if method == "ltr" and retriever.ltr_model is None:
        method = "hybrid"

    parsed = parse_query(req.message)
    # Skip retrieval for pure greetings / help
    lower = req.message.lower().strip()
    skip_search = lower in {
        "hi",
        "hello",
        "hey",
        "yo",
        "help",
        "thanks",
        "thank you",
    } or lower.startswith(("hi ", "hello ", "hey "))

    hits: list[RankedHit] = []
    if not skip_search:
        hits = retriever.search(
            req.message, method=method, top_k=req.top_k, use_filters=True
        )

    results = _scores_to_five(hits)
    reply = build_reply(req.message, parsed, results)

    return ChatResponse(
        reply=reply,
        parsed=_parsed_out(parsed),
        results=results,
        method=method,
    )
