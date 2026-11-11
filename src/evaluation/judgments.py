"""Heuristic graded relevance labels for offline evaluation.

For production you would replace this with human judgments or click logs.
Here we score restaurants against structured query intent so Recall@10 /
NDCG@10 comparisons are reproducible on the sample (or Yelp) corpus.
"""

from __future__ import annotations

import pandas as pd

from src.data.utils import as_list
from src.llm.query_parser import ParsedQuery, parse_query

# Curated evaluation queries covering multi-constraint natural language
EVAL_QUERIES = [
    "Find a quiet Italian restaurant for a date with vegetarian options",
    "Best sushi for a romantic anniversary dinner",
    "Cheap spicy vegetarian Indian food",
    "Quiet French bistro for date night with wine",
    "Loud Korean BBQ for a big group",
    "Vegan brunch spot in Oakland",
    "Upscale quiet steakhouse for a special occasion",
    "Casual ramen near Berkeley",
    "Peaceful Thai restaurant with vegetarian curry",
    "Family friendly Italian pizza place",
]


def grade_restaurant(row: pd.Series, parsed: ParsedQuery) -> int:
    """Return graded relevance 0–4."""
    score = 0
    cats = str(row.get("categories") or "").lower()
    cuisines = {str(c).lower() for c in as_list(row.get("cuisines"))}

    if parsed.cuisines:
        cuisine_hit = any(c in cuisines or c in cats for c in parsed.cuisines)
        if cuisine_hit:
            score += 2
        else:
            return 0  # wrong cuisine → non-relevant for cuisine-intent queries

    if parsed.quiet:
        score += 1 if row.get("quiet") else -1
    if parsed.romantic:
        score += 1 if row.get("romantic") else 0
    if parsed.vegetarian or parsed.vegan:
        score += 1 if row.get("vegetarian_friendly") else -1
    if parsed.price_max is not None:
        pr = int(row.get("price_range") or 0)
        if pr and pr <= parsed.price_max:
            score += 1
        elif pr and pr > parsed.price_max:
            score -= 1
    if parsed.city:
        if str(row.get("city") or "").lower() == parsed.city.lower():
            score += 1

    # Rating quality bump
    stars = float(row.get("stars") or 0)
    if stars >= 4.5:
        score += 1
    elif stars < 3.5:
        score -= 1

    return int(max(0, min(4, score)))


def build_judgment_table(docs: pd.DataFrame, queries: list[str] | None = None) -> pd.DataFrame:
    queries = queries or EVAL_QUERIES
    rows = []
    for qid, query in enumerate(queries):
        parsed = parse_query(query)
        for _, biz in docs.iterrows():
            rel = grade_restaurant(biz, parsed)
            if rel > 0:
                rows.append(
                    {
                        "qid": qid,
                        "query": query,
                        "business_id": biz["business_id"],
                        "relevance": rel,
                    }
                )
    return pd.DataFrame(rows)


def judgments_by_query(judgments: pd.DataFrame) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for query, group in judgments.groupby("query"):
        out[str(query)] = {
            str(r.business_id): float(r.relevance) for r in group.itertuples()
        }
    return out
