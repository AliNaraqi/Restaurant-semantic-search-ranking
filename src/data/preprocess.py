"""Load Yelp (or sample) JSON and build searchable restaurant documents."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import (
    BUSINESS_FILE,
    DOCS_PARQUET,
    PROCESSED_DIR,
    RESTAURANTS_PARQUET,
    REVIEW_FILE,
    REVIEWS_PARQUET,
    SAMPLE_DIR,
)


def _read_jsonl(path: Path, limit: int | None = None) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
            if limit is not None and i + 1 >= limit:
                break
    return rows


def _parse_attr_dict(raw: Any) -> dict:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return ast.literal_eval(raw)
        except (ValueError, SyntaxError):
            return {}
    return {}


def _noise_level(attrs: dict) -> str:
    raw = str(attrs.get("NoiseLevel", "")).lower()
    for level in ("very_loud", "loud", "average", "quiet"):
        if level in raw:
            return level
    return "unknown"


def _price_range(attrs: dict) -> int:
    try:
        return int(attrs.get("RestaurantsPriceRange2", 0) or 0)
    except (TypeError, ValueError):
        return 0


def _is_vegetarian_friendly(attrs: dict, categories: str) -> bool:
    cats = (categories or "").lower()
    if "vegetarian" in cats or "vegan" in cats:
        return True
    val = str(attrs.get("RestaurantsVegetarianFriendly", "")).lower()
    return val in {"true", "u'true'", "yes", "1"}


def _is_romantic_or_quiet(attrs: dict) -> tuple[bool, bool]:
    ambience = str(attrs.get("Ambience", "")).lower()
    good = str(attrs.get("GoodForMeal", "")).lower()
    noise = _noise_level(attrs)
    romantic = ("romantic" in ambience and "true" in ambience) or "datenight" in good
    quiet = noise == "quiet" or ("quiet" in ambience and "true" in ambience)
    return romantic, quiet


def _cuisine_list(categories: str) -> list[str]:
    if not categories:
        return []
    known = {
        "italian",
        "mexican",
        "japanese",
        "chinese",
        "indian",
        "thai",
        "vietnamese",
        "korean",
        "french",
        "mediterranean",
        "greek",
        "american",
        "seafood",
        "pizza",
        "sushi",
        "ramen",
        "steakhouses",
        "vegan",
        "vegetarian",
        "burgers",
        "desserts",
        "wine bars",
        "breakfast & brunch",
    }
    parts = [p.strip().lower() for p in categories.split(",")]
    return [p for p in parts if p in known or any(k in p for k in known)]


def load_businesses(path: Path | None = None, restaurant_only: bool = True) -> pd.DataFrame:
    path = path or BUSINESS_FILE
    rows = _read_jsonl(path)
    df = pd.DataFrame(rows)
    if restaurant_only and "categories" in df.columns:
        df = df[df["categories"].fillna("").str.contains("Restaurants", case=False)]
    df = df[df.get("is_open", 1) == 1].copy() if "is_open" in df.columns else df.copy()

    tags_path = SAMPLE_DIR / "business_tags.json"
    tags_map: dict[str, list[str]] = {}
    if tags_path.exists():
        tags_map = json.loads(tags_path.read_text(encoding="utf-8"))

    parsed = []
    for _, row in df.iterrows():
        attrs = row.get("attributes")
        if isinstance(attrs, str):
            try:
                attrs = json.loads(attrs)
            except json.JSONDecodeError:
                attrs = _parse_attr_dict(attrs)
        attrs = attrs or {}
        romantic, quiet = _is_romantic_or_quiet(attrs)
        cats = row.get("categories") or ""
        bid = row["business_id"]
        parsed.append(
            {
                "business_id": bid,
                "name": row.get("name", ""),
                "city": row.get("city", ""),
                "state": row.get("state", ""),
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
                "stars": float(row.get("stars") or 0),
                "review_count": int(row.get("review_count") or 0),
                "categories": cats,
                "cuisines": _cuisine_list(cats),
                "price_range": _price_range(attrs),
                "noise_level": _noise_level(attrs),
                "vegetarian_friendly": _is_vegetarian_friendly(attrs, cats),
                "romantic": romantic,
                "quiet": quiet,
                "tags": tags_map.get(bid, []),
                "attributes": attrs,
            }
        )
    return pd.DataFrame(parsed)


def load_reviews(path: Path | None = None, business_ids: set[str] | None = None) -> pd.DataFrame:
    path = path or REVIEW_FILE
    rows = _read_jsonl(path)
    df = pd.DataFrame(rows)
    if business_ids is not None:
        df = df[df["business_id"].isin(business_ids)]
    return df.reset_index(drop=True)


def build_search_documents(
    restaurants: pd.DataFrame, reviews: pd.DataFrame
) -> pd.DataFrame:
    """Concatenate name, categories, tags, and top reviews into a retrieval doc."""
    review_text = (
        reviews.sort_values("stars", ascending=False)
        .groupby("business_id")["text"]
        .apply(lambda s: " ".join(s.head(5).astype(str)))
        .rename("review_blob")
    )
    docs = restaurants.merge(review_text, on="business_id", how="left")
    docs["review_blob"] = docs["review_blob"].fillna("")

    def make_doc(r: pd.Series) -> str:
        tag_str = " ".join(r["tags"]) if isinstance(r["tags"], list) else ""
        cuisine_str = " ".join(r["cuisines"]) if isinstance(r["cuisines"], list) else ""
        flags = []
        if r["vegetarian_friendly"]:
            flags.append("vegetarian friendly vegan options")
        if r["quiet"]:
            flags.append("quiet peaceful low noise intimate")
        if r["romantic"]:
            flags.append("romantic date night candlelight")
        return " ".join(
            [
                str(r["name"]),
                str(r["categories"]),
                cuisine_str,
                tag_str,
                " ".join(flags),
                f"city {r['city']}",
                f"price {'$' * max(1, int(r['price_range'] or 1))}",
                f"rating {r['stars']}",
                r["review_blob"][:2000],
            ]
        )

    docs["document"] = docs.apply(make_doc, axis=1)
    docs["document_clean"] = docs["document"].apply(
        lambda t: re.sub(r"\s+", " ", str(t).lower()).strip()
    )
    return docs


def prepare_all(save: bool = True) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    restaurants = load_businesses()
    reviews = load_reviews(business_ids=set(restaurants["business_id"]))
    docs = build_search_documents(restaurants, reviews)

    if save:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        restaurants.to_parquet(RESTAURANTS_PARQUET, index=False)
        reviews.to_parquet(REVIEWS_PARQUET, index=False)
        docs.to_parquet(DOCS_PARQUET, index=False)
        print(f"Saved {len(restaurants)} restaurants → {RESTAURANTS_PARQUET}")
        print(f"Saved {len(reviews)} reviews → {REVIEWS_PARQUET}")
        print(f"Saved {len(docs)} search docs → {DOCS_PARQUET}")

    return restaurants, reviews, docs


if __name__ == "__main__":
    prepare_all()
