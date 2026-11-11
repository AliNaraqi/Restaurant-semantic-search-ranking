"""Pydantic request/response models for the search API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, examples=[
        "Find a quiet Italian restaurant for a date with vegetarian options"
    ])
    top_k: int = Field(default=10, ge=1, le=50)
    method: Literal["semantic", "bm25", "hybrid", "ltr"] = "ltr"
    use_filters: bool = True
    # UI ranking / location filters (override NL parse when set)
    city: str | None = Field(default=None, max_length=80)
    price_max: int | None = Field(default=None, ge=1, le=4)
    vibe: Literal["any", "quiet", "romantic", "vegetarian"] | None = "any"
    sort_by: Literal["match", "rating", "value", "quiet"] = "match"


class RestaurantResult(BaseModel):
    business_id: str
    name: str | None = None
    city: str | None = None
    stars: float | None = None
    review_count: int | None = None
    categories: str | None = None
    price_range: int | None = None
    noise_level: str | None = None
    vegetarian_friendly: bool | None = None
    quiet: bool | None = None
    romantic: bool | None = None
    cuisines: list[str] = Field(default_factory=list)
    score: float
    semantic_score: float | None = None
    bm25_score: float | None = None
    hybrid_score: float | None = None
    ltr_score: float | None = None


class ParsedQueryOut(BaseModel):
    search_text: str
    cuisines: list[str] = Field(default_factory=list)
    vegetarian: bool | None = None
    vegan: bool | None = None
    quiet: bool | None = None
    romantic: bool | None = None
    price_max: int | None = None
    city: str | None = None
    occasion: str | None = None


class SearchResponse(BaseModel):
    query: str
    method: str
    parsed: ParsedQueryOut
    results: list[RestaurantResult]


class HealthResponse(BaseModel):
    status: str
    restaurants_indexed: int
    ltr_loaded: bool
    extras: dict[str, Any] = Field(default_factory=dict)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    history: list[ChatMessage] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=10)
    method: Literal["semantic", "bm25", "hybrid", "ltr"] = "ltr"


class ChatResponse(BaseModel):
    reply: str
    parsed: ParsedQueryOut
    results: list[RestaurantResult]
    method: str

