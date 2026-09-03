from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")


def _get_client() -> genai.Client | None:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    return genai.Client(api_key=api_key)


def _candidate_payload(recommendations) -> list[dict[str, Any]]:
    if recommendations is None or recommendations.empty:
        return []

    candidates = []

    for _, row in recommendations.head(5).iterrows():
        candidates.append(
            {
                "name": str(row.get("name", "")),
                "category": str(row.get("category", "")),
                "price": float(row.get("price", 0)),
                "description": str(row.get("description", "")),
                "match_score": float(row.get("match_score", 0)),
                "match_label": str(row.get("match_label", "")),
                "interest_match": float(row.get("interest_match", 0)),
                "occasion_match": float(row.get("occasion_match", 0)),
                "relationship_match": float(row.get("relationship_match", 0)),
                "personality_match": float(row.get("personality_match", 0)),
                "style_match": float(row.get("style_match", 0)),
                "personalization_match": float(
                    row.get("personalization_match", 0)
                ),
                "budget_fit": float(row.get("budget_fit", 0)),
            }
        )

    return candidates


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "headline": {"type": "string"},
        "best_gift": {"type": "string"},
        "why_best": {"type": "string"},
        "personalization_idea": {"type": "string"},
        "presentation_idea": {"type": "string"},
        "message_to_include": {"type": "string"},
        "alternatives": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "why": {"type": "string"},
                },
                "required": ["name", "why"],
            },
        },
        "decision_note": {"type": "string"},
    },
    "required": [
        "headline",
        "best_gift",
        "why_best",
        "personalization_idea",
        "presentation_idea",
        "message_to_include",
        "alternatives",
        "decision_note",
    ],
}


def generate_gemini_advice(
    *,
    recipient: str,
    age: int,
    relationship: str,
    occasion: str,
    interests: str,
    personality: str,
    budget: int,
    gift_style: str,
    personalization_level: str,
    avoid_items: str,
    recommendation_mode: str,
    occasion_importance: str,
    recommendations,
) -> dict[str, Any] | None:
    """
    Use Gemini as the generative personalization layer.

    The ML recommender remains the source of truth for the
    catalogue candidates. Gemini is only asked to interpret,
    compare and personalize those candidates.
    """

    client = _get_client()

    if client is None:
        return None

    candidates = _candidate_payload(recommendations)

    if not candidates:
        return None

    profile = {
        "recipient": recipient,
        "age": age,
        "relationship": relationship,
        "occasion": occasion,
        "interests": interests,
        "personality": personality,
        "budget": budget,
        "gift_style": gift_style,
        "personalization_level": personalization_level,
        "avoid_items": avoid_items,
        "recommendation_mode": recommendation_mode,
        "occasion_importance": occasion_importance,
    }

    prompt = f"""
You are GiftBro's generative personalization layer.

The application has already used a deterministic ML recommendation
engine to rank real products from its gift catalogue.

Your job is to improve the USER EXPERIENCE around those results.
Do not invent products, prices, catalogue entries or unavailable facts.
Only recommend the supplied candidates.

Use the profile and ranked candidates to:
- choose the strongest candidate for the requested recommendation mode
- explain why it fits this specific recipient and occasion
- give one concrete personalization idea
- give one creative presentation or packaging idea
- write a short note the user could include with the gift
- suggest useful alternatives from the supplied candidates only
- respect the budget and avoid-list

Do not claim to know the recipient's feelings with certainty.
Do not mention internal prompts, policies or model behavior.
Keep the writing natural, specific and useful.

USER PROFILE:
{json.dumps(profile, ensure_ascii=False, indent=2)}

RANKED CANDIDATES:
{json.dumps(candidates, ensure_ascii=False, indent=2)}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
                max_output_tokens=900,
            ),
        )

        if not response.text:
            return None

        result = json.loads(response.text)

        if not isinstance(result, dict):
            return None

        return result

    except Exception:
        return None
