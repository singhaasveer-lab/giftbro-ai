from __future__ import annotations

from typing import Any

import pandas as pd


# ============================================================
# OPENING MESSAGES
# ============================================================

OPENINGS_PARTNER = [
    "Alright, Romeo. I checked the occasion, recipient profile, budget and the strongest catalogue matches. 🎁",
    "Good news. We can stop panic-shopping. I found the strongest options for this profile.",
    "Let's make this thoughtful instead of random. I've narrowed the catalogue down for you.",
]

OPENINGS_FRIEND = [
    "Let's find something thoughtful without making it look like you panic-bought it on the way there. 😂",
    "Time to upgrade from 'I needed a gift' to 'I actually know this person.'",
    "I've narrowed this down to gifts that actually fit the person, not just the occasion.",
]

OPENINGS_DEFAULT = [
    "Gift search complete. 🎁 I found the strongest matches for this profile.",
    "Let's turn the gift search into an actual recommendation instead of a catalogue scroll.",
    "I checked the profile and ranked the strongest options for you.",
]


# ============================================================
# GENERAL HELPERS
# ============================================================

def _clean(value: Any) -> str:
    """Convert a value into safe readable text."""

    return str(value or "").strip()


def _number(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _currency(value: Any) -> str:
    """Format price as a simple INR amount."""

    amount = _number(value)

    return f"₹{amount:,.0f}"


def _deterministic_opening(
    relationship: str,
    recipient: str,
    occasion: str,
) -> str:
    """
    Select a stable opening.

    The same profile produces the same opening, which keeps
    the application reproducible and easier to test.
    """

    relation = relationship.lower()

    if relation == "partner":
        pool = OPENINGS_PARTNER

    elif "friend" in relation:
        pool = OPENINGS_FRIEND

    else:
        pool = OPENINGS_DEFAULT

    seed_text = (
        f"{recipient}|"
        f"{relationship}|"
        f"{occasion}"
    )

    index = (
        sum(
            ord(char)
            for char in seed_text
        )
        % len(pool)
    )

    return pool[index]


def _match_reasons(row: pd.Series) -> list[str]:
    """
    Identify the strongest recommendation signals.
    """

    reasons: list[str] = []

    interest = _number(
        row.get("interest_match")
    )

    occasion = _number(
        row.get("occasion_match")
    )

    relationship = _number(
        row.get("relationship_match")
    )

    personality = _number(
        row.get("personality_match")
    )

    budget_fit = _number(
        row.get("budget_fit")
    )

    if interest >= 0.30:
        reasons.append("their interests")

    if occasion >= 0.80:
        reasons.append("the occasion")

    if relationship >= 0.80:
        reasons.append("your relationship")

    if personality >= 0.25:
        reasons.append("their personality")

    if budget_fit >= 0.70:
        reasons.append("your budget")

    return reasons


def _build_reason(row: pd.Series) -> str:
    """
    Build a readable explanation directly from recommendation
    signals.
    """

    reasons = _match_reasons(row)

    if not reasons:

        return (
            "This gift ranked strongly across the overall "
            "personalization score."
        )

    if len(reasons) == 1:
        joined = reasons[0]

    elif len(reasons) == 2:
        joined = (
            f"{reasons[0]} and {reasons[1]}"
        )

    else:
        joined = (
            ", ".join(reasons[:-1])
            + f", and {reasons[-1]}"
        )

    return (
        f"This recommendation matches {joined} "
        "and ranked strongly for the overall profile."
    )


def _personalization_tip(
    row: pd.Series,
) -> str:
    """
    Suggest a simple way to make the recommendation more
    personal.
    """

    name = _clean(
        row.get("name")
    ).lower()

    category = _clean(
        row.get("category")
    ).lower()

    interests = _clean(
        row.get("interests")
    ).lower()

    if any(
        word in name
        for word in [
            "photo",
            "album",
            "frame",
            "portrait",
            "camera",
            "tripod",
        ]
    ):
        return (
            "Add a favorite photo or memory and include "
            "a short note explaining why it matters."
        )

    if (
        "book" in category
        or "journal" in name
    ):
        return (
            "Write a short note inside the cover explaining "
            "why you chose this specific gift."
        )

    if (
        "jewelry" in category
        or "pendant" in name
        or "bracelet" in name
    ):
        return (
            "Add initials, a meaningful date, or a short "
            "personal message."
        )

    if (
        "beauty" in category
        or "skincare" in interests
        or "self-care" in interests
        or "self care" in interests
    ):
        return (
            "Pair it with a small item you already know "
            "they genuinely enjoy."
        )

    if "technology" in category:
        return (
            "Choose a colour, finish, or accessory that "
            "fits their everyday setup."
        )

    if "art" in category:
        return (
            "Add a small handwritten note about their "
            "creative side or a shared memory."
        )

    if "food" in category:
        return (
            "Pair it with a favourite treat or a handwritten "
            "message."
        )

    if "travel" in category:
        return (
            "Tie it to a place, trip, or travel memory "
            "you share."
        )

    if "music" in interests:
        return (
            "Add a playlist, song reference, or note about "
            "their favourite artist."
        )

    return (
        "Add a handwritten message connected to a shared "
        "memory, inside joke, or experience."
    )


def _verdict_for_score(score: float) -> str:
    """Return a readable recommendation verdict."""

    if score >= 90:
        return "Exceptional fit"

    if score >= 82:
        return "Excellent fit"

    if score >= 72:
        return "Strong fit"

    if score >= 62:
        return "Good fit"

    return "Potential fit"


def _budget_message(
    price: float,
    budget: float,
) -> str:
    """Explain how the recommendation relates to the budget."""

    if budget <= 0:
        return "Budget information was not available."

    if price <= budget:
        remaining = budget - price

        if remaining <= budget * 0.10:
            return (
                f"It uses almost all of your budget "
                f"({ _currency(remaining) } remaining)."
            )

        return (
            f"It stays within budget with "
            f"{_currency(remaining)} left."
        )

    over = price - budget

    return (
        f"It is {_currency(over)} above the selected budget."
    )


def _score_breakdown(row: pd.Series) -> dict[str, float]:
    """
    Return the transparent scoring components produced by
    the recommender.
    """

    return {
        "semantic": round(
            _number(
                row.get("semantic_component"),
            ) * 100,
            1,
        ),
        "interest": round(
            _number(
                row.get("interest_component"),
            ) * 100,
            1,
        ),
        "occasion": round(
            _number(
                row.get("occasion_component"),
            ) * 100,
            1,
        ),
        "relationship": round(
            _number(
                row.get("relationship_component"),
            ) * 100,
            1,
        ),
        "personality": round(
            _number(
                row.get("personality_component"),
            ) * 100,
            1,
        ),
        "budget": round(
            _number(
                row.get("budget_component"),
            ) * 100,
            1,
        ),
    }


def _profile_summary(
    recipient: str,
    age: Any,
    relationship: str,
    occasion: str,
    interests: str,
    personality: str,
    budget: Any,
) -> str:
    """
    Create a concise summary of the recommendation profile.
    """

    recipient_text = (
        recipient.strip()
        if recipient
        else "the recipient"
    )

    details = [
        f"Recipient: {recipient_text}",
        f"Relationship: {relationship}",
        f"Occasion: {occasion}",
        f"Interests: {interests}",
        f"Personality: {personality}",
    ]

    if age:
        details.insert(
            1,
            f"Age: {age}",
        )

    if budget:
        details.append(
            f"Budget: {_currency(budget)}"
        )

    return " · ".join(
        str(item)
        for item in details
        if item
    )


# ============================================================
# MAIN COACH
# ============================================================

def generate_gift_advice(
    recipient,
    age,
    relationship,
    occasion,
    interests,
    personality,
    budget,
    recommendations,
):
    """
    Generate GiftBro's conversational recommendation layer.

    This function is intentionally deterministic. The recommender
    performs ranking; this layer turns the ranked results into
    readable product guidance.
    """

    # --------------------------------------------------------
    # Empty-result handling
    # --------------------------------------------------------

    if (
        recommendations is None
        or recommendations.empty
    ):

        return {
            "opening": (
                "I couldn't find a strong recommendation "
                "for this profile."
            ),
            "profile_summary": _profile_summary(
                recipient,
                age,
                relationship,
                occasion,
                interests,
                personality,
                budget,
            ),
            "best": None,
            "alternatives": [],
            "pick": (
                "Try increasing the budget, adding more "
                "specific interests, or adjusting the "
                "recipient profile."
            ),
            "warning": (
                "A weak match is better treated as a signal "
                "to refine the search than as a reason to "
                "force a recommendation."
            ),
            "closing": (
                "Give me a slightly clearer profile and "
                "we can narrow it down further. 🎁"
            ),
        }

    relation = _clean(
        relationship
    ).lower()

    occasion_text = _clean(
        occasion
    )

    recipient_text = (
        _clean(recipient)
        or "the recipient"
    )

    opening = _deterministic_opening(
        relation,
        recipient_text,
        occasion_text,
    )

    # --------------------------------------------------------
    # Best recommendation
    # --------------------------------------------------------

    best_row = recommendations.iloc[0]

    best_score = _number(
        best_row.get("match_score")
    )

    best_price = _number(
        best_row.get("price")
    )

    best = {
        "rank": 1,
        "name": _clean(
            best_row.get("name")
        ),
        "category": _clean(
            best_row.get("category")
        ),
        "price": int(
            round(best_price)
        ),
        "price_display": _currency(
            best_price
        ),
        "score": round(
            best_score,
            1,
        ),
        "verdict": (
            _clean(
                best_row.get("match_label")
            )
            or _verdict_for_score(
                best_score
            )
        ),
        "description": _clean(
            best_row.get("description")
        ),
        "why": _build_reason(
            best_row
        ),
        "personalization": _personalization_tip(
            best_row
        ),
        "budget_note": _budget_message(
            best_price,
            _number(budget),
        ),
        "score_breakdown": _score_breakdown(
            best_row
        ),
    }

    # --------------------------------------------------------
    # Alternatives
    # --------------------------------------------------------

    alternatives: list[dict[str, Any]] = []

    alternative_rows = recommendations.iloc[1:4]

    for rank, (_, row) in enumerate(
        alternative_rows.iterrows(),
        start=2,
    ):

        score = _number(
            row.get("match_score")
        )

        price = _number(
            row.get("price")
        )

        alternatives.append(
            {
                "rank": rank,
                "name": _clean(
                    row.get("name")
                ),
                "category": _clean(
                    row.get("category")
                ),
                "price": int(
                    round(price)
                ),
                "price_display": _currency(
                    price
                ),
                "score": round(
                    score,
                    1,
                ),
                "verdict": (
                    _clean(
                        row.get("match_label")
                    )
                    or _verdict_for_score(
                        score
                    )
                ),
                "description": _clean(
                    row.get("description")
                ),
                "why": _build_reason(
                    row
                ),
                "personalization": _personalization_tip(
                    row
                ),
                "budget_note": _budget_message(
                    price,
                    _number(budget),
                ),
                "score_breakdown": _score_breakdown(
                    row
                ),
            }
        )

    # --------------------------------------------------------
    # Final recommendation
    # --------------------------------------------------------

    if best_score >= 85:

        pick = (
            f"Go with **{best['name']}**. "
            f"It scored {best_score:.0f}% and is the "
            "strongest overall match for this profile."
        )

    elif best_score >= 70:

        pick = (
            f"**{best['name']}** is the strongest choice "
            f"at {best_score:.0f}% and gives you the best "
            "balance across the profile."
        )

    else:

        pick = (
            f"**{best['name']}** is currently the best-ranked "
            f"option at {best_score:.0f}%, but the profile "
            "could use more detail for a stronger match."
        )

    # --------------------------------------------------------
    # Warning
    # --------------------------------------------------------

    warning = (
        "A higher price does not automatically mean a better "
        "gift. Match quality matters more than the price tag."
    )

    if best_price > _number(budget):

        warning = (
            f"The top recommendation is above the selected "
            f"budget. Consider one of the alternatives that "
            f"fits within {_currency(budget)}."
        )

    # --------------------------------------------------------
    # Closing
    # --------------------------------------------------------

    closing = (
        f"Now you have a shortlist that fits {recipient_text}, "
        f"the {occasion_text.lower()} occasion, and the profile "
        "you gave me. 🎁"
    )

    # --------------------------------------------------------
    # Profile summary
    # --------------------------------------------------------

    profile_summary = _profile_summary(
        recipient,
        age,
        relationship,
        occasion,
        interests,
        personality,
        budget,
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "opening": opening,
        "profile_summary": profile_summary,
        "best": best,
        "alternatives": alternatives,
        "pick": pick,
        "warning": warning,
        "closing": closing,
    }