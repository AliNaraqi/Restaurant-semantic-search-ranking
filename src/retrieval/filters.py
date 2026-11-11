"""Metadata filtering over restaurant DataFrame rows."""

from __future__ import annotations

import pandas as pd

from src.llm.query_parser import ParsedQuery


def apply_metadata_filters(
    df: pd.DataFrame,
    parsed: ParsedQuery,
    soft: bool = True,
) -> pd.DataFrame:
    """Filter restaurants by parsed metadata.

    soft=True keeps candidates that match most constraints (threshold = n-1)
    so hybrid recall does not collapse when one facet is noisy.
    """
    out = df.copy()
    masks: list[pd.Series] = []

    if parsed.city:
        masks.append(out["city"].str.lower() == parsed.city.lower())

    if parsed.cuisines:

        def row_cuisine(row: pd.Series) -> bool:
            raw = row.get("cuisines")
            if raw is None:
                items = []
            elif isinstance(raw, list):
                items = raw
            else:
                try:
                    items = list(raw)
                except TypeError:
                    items = []
            lower = {str(c).lower() for c in items}
            cat_blob = str(row.get("categories") or "").lower()
            return any(c in lower or c in cat_blob for c in parsed.cuisines)

        masks.append(out.apply(row_cuisine, axis=1))

    if parsed.vegetarian:
        masks.append(out["vegetarian_friendly"] == True)  # noqa: E712
    if parsed.vegan:
        masks.append(
            (out["vegetarian_friendly"] == True)  # noqa: E712
            | out["categories"].str.contains("Vegan", case=False, na=False)
        )
    if parsed.quiet:
        masks.append(out["quiet"] == True)  # noqa: E712
    if parsed.romantic:
        masks.append(out["romantic"] == True)  # noqa: E712
    if parsed.price_max is not None:
        masks.append(
            (out["price_range"] <= parsed.price_max) | (out["price_range"] == 0)
        )
    if parsed.price_min is not None:
        masks.append(out["price_range"] >= parsed.price_min)
    if parsed.min_stars is not None:
        masks.append(out["stars"] >= parsed.min_stars)

    if not masks:
        return out

    if soft:
        score = sum(m.astype(int) for m in masks)
        threshold = max(1, len(masks) - 1) if len(masks) > 1 else 1
        filtered = out[score >= threshold]
        if len(filtered) == 0:
            filtered = out[score >= 1]
        return filtered if len(filtered) else out

    combined = masks[0]
    for m in masks[1:]:
        combined = combined & m
    filtered = out[combined]
    return filtered if len(filtered) else out
