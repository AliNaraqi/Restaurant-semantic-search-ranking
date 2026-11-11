"""Central configuration for the restaurant search engine."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
SAMPLE_DIR = DATA_DIR / "sample"
PROCESSED_DIR = DATA_DIR / "processed"
INDEX_DIR = DATA_DIR / "indexes"
MODEL_DIR = PROJECT_ROOT / "models"

for _d in (RAW_DIR, SAMPLE_DIR, PROCESSED_DIR, INDEX_DIR, MODEL_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Prefer real Yelp dump if present; otherwise fall back to sample data
BUSINESS_FILE = (
    RAW_DIR / "yelp_academic_dataset_business.json"
    if (RAW_DIR / "yelp_academic_dataset_business.json").exists()
    else SAMPLE_DIR / "businesses.jsonl"
)
REVIEW_FILE = (
    RAW_DIR / "yelp_academic_dataset_review.json"
    if (RAW_DIR / "yelp_academic_dataset_review.json").exists()
    else SAMPLE_DIR / "reviews.jsonl"
)

RESTAURANTS_PARQUET = PROCESSED_DIR / "restaurants.parquet"
REVIEWS_PARQUET = PROCESSED_DIR / "reviews.parquet"
DOCS_PARQUET = PROCESSED_DIR / "search_docs.parquet"

FAISS_INDEX_PATH = INDEX_DIR / "faiss.index"
EMBEDDINGS_PATH = INDEX_DIR / "embeddings.npy"
DOC_IDS_PATH = INDEX_DIR / "doc_ids.json"
BM25_PATH = INDEX_DIR / "bm25.pkl"
LTR_MODEL_PATH = MODEL_DIR / "ltr_lightgbm.txt"
EVAL_RESULTS_PATH = PROCESSED_DIR / "eval_results.json"

# ---------------------------------------------------------------------------
# Model / retrieval settings
# ---------------------------------------------------------------------------
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
EMBEDDING_DIM = 384
FAISS_TOP_K = 50
BM25_TOP_K = 50
HYBRID_TOP_K = 50
FINAL_TOP_K = 10

# Hybrid fusion weights (before LTR re-rank)
SEMANTIC_WEIGHT = float(os.getenv("SEMANTIC_WEIGHT", "0.55"))
BM25_WEIGHT = float(os.getenv("BM25_WEIGHT", "0.45"))

# LLM for natural-language query parsing
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
