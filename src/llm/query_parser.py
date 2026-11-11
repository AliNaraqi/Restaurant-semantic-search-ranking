"""Parse natural-language restaurant queries into structured filters + search text.

Uses an LLM when OPENAI_API_KEY is set; otherwise a deterministic rule-based fallback.
"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field

from src.config import LLM_MODEL, OPENAI_API_KEY, OPENAI_BASE_URL


class ParsedQuery(BaseModel):
    raw_query: str
    search_text: str = Field(
        description="Cleaned semantic search string (cuisine + intent, no filter words stripped hard)"
    )
    cuisines: list[str] = Field(default_factory=list)
    vegetarian: bool | None = None
    vegan: bool | None = None
    quiet: bool | None = None
    romantic: bool | None = None
    price_max: int | None = Field(default=None, ge=1, le=4)
    price_min: int | None = Field(default=None, ge=1, le=4)
    city: str | None = None
    min_stars: float | None = None
    occasion: str | None = None


CUISINE_ALIASES = {
    "italian": "italian",
    "pasta": "italian",
    "pizza": "pizza",
    "mexican": "mexican",
    "taco": "mexican",
    "tacos": "mexican",
    "japanese": "japanese",
    "sushi": "sushi",
    "ramen": "ramen",
    "chinese": "chinese",
    "dim sum": "chinese",
    "indian": "indian",
    "thai": "thai",
    "vietnamese": "vietnamese",
    "pho": "vietnamese",
    "korean": "korean",
    "bbq": "korean",
    "french": "french",
    "mediterranean": "mediterranean",
    "greek": "greek",
    "seafood": "seafood",
    "steak": "steakhouses",
    "steakhouse": "steakhouses",
    "burger": "burgers",
    "vegan": "vegan",
    "brunch": "breakfast & brunch",
    "breakfast": "breakfast & brunch",
}


def _rule_based_parse(query: str) -> ParsedQuery:
    q = query.lower()
    cuisines: list[str] = []
    for alias, canon in CUISINE_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", q):
            if canon not in cuisines:
                cuisines.append(canon)

    vegetarian = True if re.search(r"\bvegetarian\b|\bveggie\b", q) else None
    vegan = True if re.search(r"\bvegan\b|\bplant[- ]based\b", q) else None
    quiet = True if re.search(r"\bquiet\b|\bpeaceful\b|\bintimate\b|\blow[- ]noise\b", q) else None
    romantic = (
        True
        if re.search(r"\bromantic\b|\bdate\b|\bdatenight\b|\bcandlelight\b|\banniversary\b", q)
        else None
    )

    price_max = None
    if re.search(r"\bcheap\b|\binexpensive\b|\bbudget\b", q):
        price_max = 2
    elif re.search(r"\bupscale\b|\bfine dining\b|\bluxury\b", q):
        price_max = 4

    city = None
    city_aliases = (
        ("quebec city", "Quebec City"),
        ("québec city", "Quebec City"),
        ("toronto", "Toronto"),
        ("vancouver", "Vancouver"),
        ("montreal", "Montreal"),
        ("montréal", "Montreal"),
        ("calgary", "Calgary"),
        ("ottawa", "Ottawa"),
        ("edmonton", "Edmonton"),
        ("winnipeg", "Winnipeg"),
        ("halifax", "Halifax"),
        ("victoria", "Victoria"),
    )
    for alias, canon in city_aliases:
        if alias in q:
            city = canon
            break

    occasion = None
    if romantic:
        occasion = "date"
    elif re.search(r"\bgroup\b|\bfamily\b|\bparty\b", q):
        occasion = "group"

    return ParsedQuery(
        raw_query=query,
        search_text=query,
        cuisines=cuisines,
        vegetarian=vegetarian,
        vegan=vegan,
        quiet=quiet,
        romantic=romantic,
        price_max=price_max,
        city=city,
        occasion=occasion,
    )


def _llm_parse(query: str) -> ParsedQuery | None:
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        schema_hint = ParsedQuery.model_json_schema()
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract restaurant search filters from the user query. "
                        "Return JSON matching this schema keys: "
                        f"{json.dumps(list(schema_hint['properties'].keys()))}. "
                        "cuisines should be lowercase. Use null for unknown booleans/fields. "
                        "search_text should keep the semantic intent for embedding search."
                    ),
                },
                {"role": "user", "content": query},
            ],
        )
        data: dict[str, Any] = json.loads(resp.choices[0].message.content or "{}")
        data["raw_query"] = query
        if not data.get("search_text"):
            data["search_text"] = query
        return ParsedQuery.model_validate(data)
    except Exception as exc:  # noqa: BLE001 — fall back gracefully
        print(f"[query_parser] LLM parse failed ({exc}); using rules.")
        return None


def parse_query(query: str) -> ParsedQuery:
    """Parse a natural-language query into structured filters."""
    parsed = _llm_parse(query)
    if parsed is not None:
        return parsed
    return _rule_based_parse(query)
