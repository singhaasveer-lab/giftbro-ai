from __future__ import annotations

from pathlib import Path
import re
from typing import Iterable, Optional

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "gifts.csv"

REQUIRED_COLUMNS = [
    "name",
    "category",
    "occasion",
    "relationship",
    "interests",
    "personality",
    "price",
    "description",
]

TEXT_COLUMNS = [
    "name",
    "category",
    "occasion",
    "relationship",
    "interests",
    "personality",
    "description",
]

WEIGHTS = {
    "semantic": 0.20,
    "interest": 0.20,
    "occasion": 0.15,
    "relationship": 0.12,
    "personality": 0.10,
    "style": 0.08,
    "personalization": 0.05,
    "budget": 0.10,
}


# ============================================================
# DATA LOADING
# ============================================================

def load_gifts() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {DATA_FILE.name} in {BASE_DIR}"
        )

    df = pd.read_csv(DATA_FILE)

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "gifts.csv is missing columns: "
            + ", ".join(missing)
        )

    df = df.copy()

    for column in TEXT_COLUMNS:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce",
    ).fillna(0.0)

    df = df[df["price"] >= 0].copy()

    df = df.drop_duplicates(
        subset=[
            "name",
            "category",
            "occasion",
            "relationship",
            "price",
        ],
        keep="first",
    )

    return df.reset_index(drop=True)


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(value: object) -> str:
    text = str(value or "").lower()

    text = re.sub(
        r"[/_,&]+",
        " ",
        text,
    )

    text = re.sub(
        r"[^a-z0-9\s-]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def tokens(value: object) -> set[str]:
    text = normalize_text(value)

    if not text:
        return set()

    return set(
        re.findall(
            r"[a-z0-9]+",
            text,
        )
    )


def overlap(
    user_text: object,
    gift_text: object,
) -> float:
    user_tokens = tokens(user_text)
    gift_tokens = tokens(gift_text)

    if not user_tokens or not gift_tokens:
        return 0.0

    intersection = user_tokens & gift_tokens
    union = user_tokens | gift_tokens

    if not union:
        return 0.0

    return len(intersection) / len(union)


def context_match(
    user_value: object,
    gift_value: object,
) -> float:
    user = normalize_text(user_value)
    gift = normalize_text(gift_value)

    if not user or not gift:
        return 0.0

    if user == gift:
        return 1.0

    if user in gift or gift in user:
        return 0.85

    return overlap(
        user,
        gift,
    )


# ============================================================
# INTEREST + PERSONALITY
# ============================================================

def interest_match_score(
    user_interests: str,
    gift_interests: str,
) -> float:
    user_tokens = tokens(user_interests)
    gift_tokens = tokens(gift_interests)

    if not user_tokens or not gift_tokens:
        return 0.0

    matched = user_tokens & gift_tokens

    if not matched:
        return 0.0

    return min(
        1.0,
        len(matched) / len(user_tokens),
    )


def personality_match_score(
    user_personality: str,
    gift_personality: str,
) -> float:
    user_tokens = tokens(user_personality)
    gift_tokens = tokens(gift_personality)

    if not user_tokens or not gift_tokens:
        return 0.0

    matched = user_tokens & gift_tokens

    return min(
        1.0,
        len(matched) / len(user_tokens),
    )


# ============================================================
# GIFT STYLE
# ============================================================

STYLE_KEYWORDS = {
    "practical": [
        "technology",
        "accessories",
        "travel",
        "productivity",
        "organization",
        "fitness",
        "useful",
        "utility",
    ],
    "sentimental": [
        "photo",
        "album",
        "frame",
        "memory",
        "personalized",
        "custom",
        "jewelry",
        "journal",
        "book",
    ],
    "fun": [
        "gaming",
        "entertainment",
        "food",
        "chocolate",
        "game",
        "art",
        "creative",
    ],
    "luxury": [
        "luxury",
        "premium",
        "elegant",
        "jewelry",
        "artisan",
    ],
    "creative": [
        "art",
        "painting",
        "calligraphy",
        "creative",
        "sketch",
        "design",
        "drawing",
    ],
}


def style_match_score(
    row: pd.Series,
    gift_style: str,
) -> float:
    style = normalize_text(gift_style)

    if not style or style == "surprise me":
        return 0.65

    keywords = STYLE_KEYWORDS.get(
        style,
        [],
    )

    combined = " ".join(
        [
            normalize_text(row.get("name", "")),
            normalize_text(row.get("category", "")),
            normalize_text(row.get("description", "")),
            normalize_text(row.get("personality", "")),
            normalize_text(row.get("interests", "")),
        ]
    )

    if not keywords:
        return overlap(
            style,
            combined,
        )

    matched = sum(
        keyword in combined
        for keyword in keywords
    )

    if matched == 0:
        return 0.0

    return min(
        1.0,
        0.35 + matched * 0.14,
    )


# ============================================================
# PERSONALIZATION
# ============================================================

PERSONALIZATION_KEYWORDS = [
    "personalized",
    "personalised",
    "custom",
    "handcrafted",
    "photo",
    "album",
    "frame",
    "engraved",
    "journal",
    "memory",
]


def personalization_match_score(
    row: pd.Series,
    level: str,
) -> float:
    preference = normalize_text(level)

    if preference == "low":
        return 0.65

    combined = " ".join(
        [
            normalize_text(row.get("name", "")),
            normalize_text(row.get("description", "")),
            normalize_text(row.get("category", "")),
        ]
    )

    matches = sum(
        keyword in combined
        for keyword in PERSONALIZATION_KEYWORDS
    )

    base = min(
        1.0,
        0.30 + matches * 0.10,
    )

    if preference == "high":
        return base

    if preference == "medium":
        return min(
            1.0,
            0.55 + base * 0.35,
        )

    return base


# ============================================================
# AVOID FILTER
# ============================================================

def matches_avoid_list(
    row: pd.Series,
    avoid_items: str,
) -> bool:
    avoid_tokens = tokens(
        avoid_items
    )

    if not avoid_tokens:
        return False

    gift_text = " ".join(
        [
            normalize_text(row.get("name", "")),
            normalize_text(row.get("category", "")),
            normalize_text(row.get("description", "")),
            normalize_text(row.get("interests", "")),
        ]
    )

    gift_tokens = tokens(
        gift_text
    )

    return bool(
        avoid_tokens & gift_tokens
    )


# ============================================================
# BUDGET
# ============================================================

def budget_fit_score(
    price: float,
    budget: float,
) -> float:

    if budget <= 0:
        return 0.0

    if price > budget:
        return 0.0

    ratio = price / budget

    if ratio >= 0.70:
        return 1.0

    return max(
        0.55,
        ratio / 0.70,
    )


# ============================================================
# MATCH LABEL
# ============================================================

def match_label(
    score: float,
) -> str:

    if score >= 90:
        return "Exceptional match"

    if score >= 82:
        return "Excellent match"

    if score >= 72:
        return "Strong match"

    if score >= 60:
        return "Good match"

    return "Potential match"


# ============================================================
# EXPLANATION
# ============================================================

def build_reason(
    row: pd.Series,
) -> str:

    reasons = []

    if row["occasion_match"] >= 0.80:
        reasons.append(
            "the exact occasion"
        )

    if row["relationship_match"] >= 0.80:
        reasons.append(
            "your relationship"
        )

    if row["interest_match"] >= 0.30:
        reasons.append(
            "their interests"
        )

    if row["personality_match"] >= 0.25:
        reasons.append(
            "their personality"
        )

    if row["style_match"] >= 0.70:
        reasons.append(
            "your preferred gift style"
        )

    if row["personalization_match"] >= 0.65:
        reasons.append(
            "your personalization preference"
        )

    if row["budget_fit"] >= 0.70:
        reasons.append(
            "your budget"
        )

    if not reasons:
        return (
            "This gift ranked strongly across "
            "the overall profile."
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
        f"This gift is strongly aligned with "
        f"{joined}."
    )


def personalization_tip(
    row: pd.Series,
) -> str:

    name = normalize_text(
        row.get("name", "")
    )

    category = normalize_text(
        row.get("category", "")
    )

    interests = normalize_text(
        row.get("interests", "")
    )

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
            "Add a favourite photo or shared memory "
            "and include a short handwritten note."
        )

    if (
        "book" in category
        or "journal" in name
    ):
        return (
            "Write a personal note inside the cover "
            "explaining why you chose it."
        )

    if (
        "jewelry" in category
        or "pendant" in name
        or "bracelet" in name
    ):
        return (
            "Add initials, a meaningful date, or "
            "a short personal message."
        )

    if (
        "beauty" in category
        or "skincare" in interests
        or "self care" in interests
    ):
        return (
            "Pair it with a small item they already "
            "enjoy using."
        )

    if "technology" in category:
        return (
            "Choose a finish or accessory that "
            "matches their everyday setup."
        )

    if "art" in category:
        return (
            "Add a short note about their creativity "
            "or a shared memory."
        )

    if "food" in category:
        return (
            "Pair it with a favourite treat or a "
            "handwritten message."
        )

    if "travel" in category:
        return (
            "Connect it to a place, trip, or travel "
            "memory you share."
        )

    return (
        "Add a handwritten message connected to "
        "a shared memory or inside joke."
    )


# ============================================================
# MODE BONUS
# ============================================================

def mode_bonus(
    df: pd.DataFrame,
    mode: str,
    budget: float,
) -> pd.Series:

    result = pd.Series(
        0.0,
        index=df.index,
    )

    mode = normalize_text(
        mode
    )

    if mode == "best value":

        price_ratio = (
            df["price"]
            / max(budget, 1.0)
        ).clip(
            0,
            1,
        )

        value_score = (
            df["raw_score"] * 0.75
            + (1 - price_ratio) * 0.25
        )

        return value_score * 0.10

    if mode == "most personal":

        return (
            df["personalization_match"] * 0.08
            + df["interest_match"] * 0.06
            + df["personality_match"] * 0.04
        )

    if mode == "most unique":

        text = (
            df["name"]
            + " "
            + df["description"]
        ).str.lower()

        unique = pd.Series(
            0.0,
            index=df.index,
        )

        for keyword in [
            "custom",
            "personalized",
            "personalised",
            "handcrafted",
            "artisan",
            "limited",
            "luxury",
            "unique",
        ]:
            unique += (
                text.str.contains(
                    keyword,
                    regex=False,
                ).astype(float)
            )

        return unique.clip(
            0,
            1,
        ) * 0.12

    return result


# ============================================================
# DIVERSITY
# ============================================================

def apply_category_diversity(
    df: pd.DataFrame,
    top_n: int,
) -> pd.DataFrame:

    if df.empty:
        return df

    selected = []
    seen = set()

    for index, row in df.iterrows():

        category = normalize_text(
            row.get("category", "")
        )

        if (
            category
            and category not in seen
        ):
            selected.append(index)
            seen.add(category)

        if len(selected) >= top_n:
            break

    if len(selected) < top_n:

        for index in df.index:

            if index in selected:
                continue

            selected.append(index)

            if len(selected) >= top_n:
                break

    return (
        df.loc[selected]
        .reset_index(drop=True)
    )


# ============================================================
# MAIN RECOMMENDER
# ============================================================

def recommend_gifts(
    occasion: str,
    relationship: str,
    interests: str,
    personality: str,
    budget: int,
    top_n: int = 6,
    exclude_names: Optional[
        Iterable[str]
    ] = None,
    gift_style: str = "Surprise Me",
    personalization_level: str = "Medium",
    avoid_items: str = "",
    recommendation_mode: str = "Best Overall",
    occasion_importance: str = "Important",
) -> pd.DataFrame:

    if top_n <= 0:
        raise ValueError(
            "top_n must be greater than zero."
        )

    try:
        budget = float(budget)
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "budget must be a valid number."
        ) from exc

    if budget <= 0:
        raise ValueError(
            "budget must be greater than zero."
        )

    gifts = load_gifts()

    # --------------------------------------------------------
    # Exclusions
    # --------------------------------------------------------

    if exclude_names:

        excluded = {
            normalize_text(name)
            for name in exclude_names
            if normalize_text(name)
        }

        gifts = gifts[
            ~gifts["name"]
            .apply(normalize_text)
            .isin(excluded)
        ].copy()

    if gifts.empty:
        gifts = load_gifts()

    # --------------------------------------------------------
    # Avoid items
    # --------------------------------------------------------

    if avoid_items.strip():

        filtered = gifts[
            ~gifts.apply(
                lambda row: matches_avoid_list(
                    row,
                    avoid_items,
                ),
                axis=1,
            )
        ].copy()

        # Only apply the exclusion if some candidates remain.
        if not filtered.empty:
            gifts = filtered

    # --------------------------------------------------------
    # Feature text
    # --------------------------------------------------------

    gifts["feature_text"] = (
        gifts["name"]
        + " "
        + gifts["category"]
        + " "
        + gifts["occasion"]
        + " "
        + gifts["relationship"]
        + " "
        + gifts["interests"]
        + " "
        + gifts["personality"]
        + " "
        + gifts["description"]
    )

    user_profile = " ".join(
        [
            normalize_text(occasion),
            normalize_text(relationship),
            normalize_text(interests),
            normalize_text(personality),
            normalize_text(gift_style),
        ]
    ).strip()

    # --------------------------------------------------------
    # TF-IDF
    # --------------------------------------------------------

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
        max_features=15000,
    )

    gift_matrix = vectorizer.fit_transform(
        gifts["feature_text"]
    )

    user_vector = vectorizer.transform(
        [user_profile]
    )

    gifts["cosine_score"] = (
        cosine_similarity(
            user_vector,
            gift_matrix,
        )
        .flatten()
        .clip(0, 1)
    )

    # --------------------------------------------------------
    # Budget pool
    # --------------------------------------------------------

    affordable = gifts[
        gifts["price"] <= budget
    ].copy()

    if affordable.empty:

        affordable = (
            gifts
            .sort_values(
                "price",
                ascending=True,
            )
            .head(
                max(
                    top_n * 3,
                    12,
                )
            )
            .copy()
        )

    # --------------------------------------------------------
    # Signals
    # --------------------------------------------------------

    affordable["occasion_match"] = (
        affordable["occasion"]
        .apply(
            lambda value: context_match(
                occasion,
                value,
            )
        )
    )

    affordable["relationship_match"] = (
        affordable["relationship"]
        .apply(
            lambda value: context_match(
                relationship,
                value,
            )
        )
    )

    affordable["interest_match"] = (
        affordable["interests"]
        .apply(
            lambda value: interest_match_score(
                interests,
                value,
            )
        )
    )

    affordable["personality_match"] = (
        affordable["personality"]
        .apply(
            lambda value: personality_match_score(
                personality,
                value,
            )
        )
    )

    affordable["style_match"] = (
        affordable.apply(
            lambda row: style_match_score(
                row,
                gift_style,
            ),
            axis=1,
        )
    )

    affordable["personalization_match"] = (
        affordable.apply(
            lambda row: personalization_match_score(
                row,
                personalization_level,
            ),
            axis=1,
        )
    )

    affordable["budget_fit"] = (
        affordable.apply(
            lambda row: budget_fit_score(
                row["price"],
                budget,
            ),
            axis=1,
        )
    )

    # --------------------------------------------------------
    # Components
    # --------------------------------------------------------

    affordable["semantic_component"] = (
        affordable["cosine_score"]
        * WEIGHTS["semantic"]
    )

    affordable["interest_component"] = (
        affordable["interest_match"]
        * WEIGHTS["interest"]
    )

    affordable["occasion_component"] = (
        affordable["occasion_match"]
        * WEIGHTS["occasion"]
    )

    affordable["relationship_component"] = (
        affordable["relationship_match"]
        * WEIGHTS["relationship"]
    )

    affordable["personality_component"] = (
        affordable["personality_match"]
        * WEIGHTS["personality"]
    )

    affordable["style_component"] = (
        affordable["style_match"]
        * WEIGHTS["style"]
    )

    affordable["personalization_component"] = (
        affordable["personalization_match"]
        * WEIGHTS["personalization"]
    )

    affordable["budget_component"] = (
        affordable["budget_fit"]
        * WEIGHTS["budget"]
    )

    affordable["raw_score"] = (
        affordable["semantic_component"]
        + affordable["interest_component"]
        + affordable["occasion_component"]
        + affordable["relationship_component"]
        + affordable["personality_component"]
        + affordable["style_component"]
        + affordable["personalization_component"]
        + affordable["budget_component"]
    )

    # --------------------------------------------------------
    # Recommendation mode
    # --------------------------------------------------------

    affordable["mode_bonus"] = mode_bonus(
        affordable,
        recommendation_mode,
        budget,
    )

    affordable["raw_score"] = (
        affordable["raw_score"]
        + affordable["mode_bonus"]
    )

    # --------------------------------------------------------
    # Strong-context bonus
    # --------------------------------------------------------

    affordable["context_bonus"] = (
        affordable["occasion_match"]
        * affordable["relationship_match"]
        * 0.12
    )

    affordable["raw_score"] = (
        affordable["raw_score"]
        + affordable["context_bonus"]
    ).clip(
        0,
        1,
    )

    # --------------------------------------------------------
    # OCCASION IMPORTANCE COMPONENT
    #
    # This column is deliberately created here so the final
    # output schema can never reference a missing column.
    # --------------------------------------------------------

    affordable["occasion_importance_match"] = (
        affordable["occasion_match"]
        * 1.0
    )

    affordable["occasion_importance_component"] = (
        affordable["occasion_importance_match"]
        * 1.0
    )

    # --------------------------------------------------------
    # Ranking
    # --------------------------------------------------------

    affordable = affordable.sort_values(
        by=[
            "raw_score",
            "occasion_match",
            "relationship_match",
            "interest_match",
            "personality_match",
            "budget_fit",
        ],
        ascending=False,
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # User-facing match score
    # --------------------------------------------------------

    affordable["match_score"] = (
        affordable["raw_score"]
        * 100
    ).clip(
        0,
        100,
    ).round(1)

    affordable["match_label"] = (
        affordable["match_score"]
        .apply(match_label)
    )

    # --------------------------------------------------------
    # Explanations
    # --------------------------------------------------------

    affordable["why"] = affordable.apply(
        build_reason,
        axis=1,
    )

    affordable["personalization"] = (
        affordable.apply(
            personalization_tip,
            axis=1,
        )
    )

    # --------------------------------------------------------
    # Transparent breakdown
    # --------------------------------------------------------

    affordable["score_breakdown"] = affordable.apply(
        lambda row: (
            f"Semantic "
            f"{row['semantic_component'] * 100:.1f}% | "
            f"Interests "
            f"{row['interest_component'] * 100:.1f}% | "
            f"Occasion "
            f"{row['occasion_component'] * 100:.1f}% | "
            f"Relationship "
            f"{row['relationship_component'] * 100:.1f}% | "
            f"Personality "
            f"{row['personality_component'] * 100:.1f}% | "
            f"Style "
            f"{row['style_component'] * 100:.1f}% | "
            f"Personalization "
            f"{row['personalization_component'] * 100:.1f}% | "
            f"Budget "
            f"{row['budget_component'] * 100:.1f}%"
        ),
        axis=1,
    )

    # --------------------------------------------------------
    # Diversity
    # --------------------------------------------------------

    affordable = apply_category_diversity(
        affordable,
        top_n,
    )

    # --------------------------------------------------------
    # FINAL OUTPUT
    #
    # Every column listed here is explicitly created above.
    # --------------------------------------------------------

    output_columns = [
        "name",
        "category",
        "occasion",
        "relationship",
        "interests",
        "personality",
        "price",
        "description",

        "match_score",
        "match_label",

        "cosine_score",

        "occasion_match",
        "occasion_importance_match",
        "occasion_importance_component",

        "relationship_match",
        "interest_match",
        "personality_match",
        "style_match",
        "personalization_match",
        "budget_fit",

        "semantic_component",
        "interest_component",
        "occasion_component",
        "relationship_component",
        "personality_component",
        "style_component",
        "personalization_component",
        "budget_component",

        "mode_bonus",
        "context_bonus",

        "why",
        "personalization",
        "score_breakdown",
    ]

    # Defensive check. This makes the error much more useful
    # if a future edit accidentally removes a required column.
    missing_output_columns = [
        column
        for column in output_columns
        if column not in affordable.columns
    ]

    if missing_output_columns:
        raise RuntimeError(
            "Recommendation output is missing columns: "
            + ", ".join(missing_output_columns)
        )

    return (
        affordable[
            output_columns
        ]
        .head(top_n)
        .reset_index(drop=True)
    )