"""Conversational restaurant assistant replies (template + optional LLM)."""

from __future__ import annotations

from src.api.schemas import RestaurantResult
from src.config import LLM_MODEL, OPENAI_API_KEY, OPENAI_BASE_URL
from src.llm.query_parser import ParsedQuery


def _price_label(n: int | None) -> str:
    if not n:
        return ""
    return "$" * min(4, max(1, int(n)))


def _format_hit(r: RestaurantResult, i: int) -> str:
    bits = [f"{i}. {r.name or r.business_id}"]
    if r.stars is not None:
        bits.append(f"{r.stars:.1f}★")
    if r.city:
        bits.append(r.city)
    if r.price_range:
        bits.append(_price_label(r.price_range))
    flags = []
    if r.quiet:
        flags.append("quiet")
    if r.romantic:
        flags.append("great for dates")
    if r.vegetarian_friendly:
        flags.append("vegetarian-friendly")
    line = " · ".join(bits)
    if flags:
        line += f" ({', '.join(flags)})"
    return line


def build_reply(
    message: str,
    parsed: ParsedQuery,
    results: list[RestaurantResult],
) -> str:
    """Build a friendly chatbot reply; uses LLM when configured, else templates."""
    llm = _llm_reply(message, parsed, results)
    if llm:
        return llm
    return _template_reply(message, parsed, results)


def _template_reply(
    message: str,
    parsed: ParsedQuery,
    results: list[RestaurantResult],
) -> str:
    lower = message.lower().strip()
    greetings = {"hi", "hello", "hey", "yo", "good morning", "good evening"}
    if lower in greetings or lower.startswith(("hi ", "hello ", "hey ")):
        return (
            "Hey! I'm FoodBot. Tell me what you're craving — cuisine, vibe, "
            "budget, or occasion — and I'll find restaurants for you."
        )

    if any(w in lower for w in ("help", "what can you", "how do")):
        return (
            "Ask me like you'd ask a friend. Try:\n"
            "• quiet Italian for a date with vegetarian options\n"
            "• cheap spicy Indian food\n"
            "• romantic sushi anniversary dinner"
        )

    if not results:
        return (
            "I couldn't find a strong match for that. "
            "Try adding a cuisine (Italian, sushi, Thai…) or a vibe (quiet, date night, cheap)."
        )

    intent_bits = []
    if parsed.cuisines:
        intent_bits.append("/".join(parsed.cuisines))
    if parsed.quiet:
        intent_bits.append("quiet")
    if parsed.romantic:
        intent_bits.append("date-night")
    if parsed.vegetarian or parsed.vegan:
        intent_bits.append("vegetarian-friendly")
    if parsed.city:
        intent_bits.append(f"in {parsed.city}")
    intent = ", ".join(intent_bits) if intent_bits else "your request"

    lines = [f"Here are my top picks for {intent}:", ""]
    for i, r in enumerate(results[:5], start=1):
        lines.append(_format_hit(r, i))
    lines.append("")
    lines.append("Want me to narrow by price, city, or noise level?")
    return "\n".join(lines)


def _llm_reply(
    message: str,
    parsed: ParsedQuery,
    results: list[RestaurantResult],
) -> str | None:
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI

        catalog = "\n".join(_format_hit(r, i) for i, r in enumerate(results[:5], start=1)) or "None"
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            temperature=0.4,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are FoodBot, a concise restaurant concierge. "
                        "Recommend only from the provided search results. "
                        "Keep replies under 120 words. Use a warm, helpful tone. "
                        "Mention star ratings when useful."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"User said: {message}\n"
                        f"Parsed intent: {parsed.model_dump()}\n"
                        f"Results:\n{catalog}\n"
                        "Write the assistant reply."
                    ),
                },
            ],
        )
        text = (resp.choices[0].message.content or "").strip()
        return text or None
    except Exception:  # noqa: BLE001
        return None
