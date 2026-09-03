from __future__ import annotations

import urllib.parse

import streamlit as st

from recommender import recommend_gifts
from ai_coach import generate_gift_advice
from database import (
    initialize_database,
    save_recommendation,
    save_favorite,
    get_favorites,
    delete_favorite,
    favorite_exists,
    get_history,
)
from gemini_service import generate_gemini_advice


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="GiftBro AI",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

initialize_database()


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "page": "home",
    "recommendations": None,
    "advice": None,
    "gemini_advice": None,
    "profile": None,
    "selected_gift": None,
    "generation_number": 0,
}

for key, value in DEFAULT_STATE.items():
    st.session_state.setdefault(key, value)


# ============================================================
# HELPERS
# ============================================================

def go_to(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def personality_text(value) -> str:
    if isinstance(value, list):
        return " ".join(str(item) for item in value).strip() or "Practical"
    return str(value or "").strip() or "Practical"


def safe_number(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value) -> str:
    return f"₹{safe_number(value):,.0f}"


def shop_url(gift_name: str, store: str = "amazon") -> str:
    query = urllib.parse.quote_plus(str(gift_name))

    if store == "amazon":
        return f"https://www.amazon.in/s?k={query}"

    return f"https://www.google.com/search?tbm=shop&q={query}"


def calculate_budget_fit(gift_price, budget) -> float:
    """Calculate display-only budget fit without relying on a DataFrame key."""
    price = safe_number(gift_price)
    limit = safe_number(budget)

    if limit <= 0:
        return 0.0

    if price > limit:
        return 0.0

    return min(1.0, price / limit)


# ============================================================
# RECOMMENDATION PIPELINE
# ============================================================

def create_search(
    recipient,
    age,
    relationship,
    occasion,
    interests,
    personality,
    budget,
    gift_style="Surprise Me",
    personalization_level="Medium",
    avoid_items="",
    recommendation_mode="Best Overall",
    occasion_importance="Important",
    exclude_names=None,
) -> None:

    p_text = personality_text(personality)

    recommendations = recommend_gifts(
        occasion=occasion,
        relationship=relationship,
        interests=interests,
        personality=p_text,
        budget=int(budget),
        top_n=6,
        exclude_names=exclude_names,
        gift_style=gift_style,
        personalization_level=personalization_level,
        avoid_items=avoid_items,
        recommendation_mode=recommendation_mode,
        occasion_importance=occasion_importance,
    )

    advice = generate_gift_advice(
        recipient=recipient,
        age=int(age),
        relationship=relationship,
        occasion=occasion,
        interests=interests,
        personality=p_text,
        budget=int(budget),
        recommendations=recommendations,
    )

    st.session_state.recommendations = recommendations
    st.session_state.advice = advice

    # Important: initial search stays fast.
    # Gemini runs only when the user explicitly asks for it.
    st.session_state.gemini_advice = None

    st.session_state.profile = {
        "recipient": recipient,
        "age": int(age),
        "relationship": relationship,
        "occasion": occasion,
        "interests": interests,
        "personality": p_text,
        "budget": int(budget),
        "gift_style": gift_style,
        "personalization_level": personalization_level,
        "avoid_items": avoid_items,
        "recommendation_mode": recommendation_mode,
        "occasion_importance": occasion_importance,
    }

    selected_gifts = ", ".join(
        recommendations["name"].astype(str).tolist()
    )

    save_recommendation(
        recipient=recipient,
        age=int(age),
        relationship=relationship,
        occasion=occasion,
        interests=interests,
        personality=p_text,
        budget=int(budget),
        selected_gifts=selected_gifts,
    )


def ask_gemini() -> None:
    profile = st.session_state.get("profile")
    recommendations = st.session_state.get("recommendations")

    if not profile or recommendations is None:
        return

    with st.spinner("✨ Gemini is cooking the final recommendation..."):
        result = generate_gemini_advice(
            recipient=profile["recipient"],
            age=profile["age"],
            relationship=profile["relationship"],
            occasion=profile["occasion"],
            interests=profile["interests"],
            personality=profile["personality"],
            budget=profile["budget"],
            gift_style=profile["gift_style"],
            personalization_level=profile["personalization_level"],
            avoid_items=profile["avoid_items"],
            recommendation_mode=profile["recommendation_mode"],
            occasion_importance=profile["occasion_importance"],
            recommendations=recommendations,
        )

    st.session_state.gemini_advice = result
    st.rerun()


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>
.stApp {
    background:
        radial-gradient(circle at 8% 0%, rgba(190,160,250,.22), transparent 25%),
        radial-gradient(circle at 95% 5%, rgba(222,201,255,.25), transparent 25%),
        linear-gradient(180deg, #f6f0ff 0%, #fbf9ff 45%, #ffffff 72%, #f7f0ff 100%);
    color: #342844;
}

.main .block-container {
    max-width: 1220px;
    padding-top: 18px;
    padding-bottom: 80px;
}

#MainMenu,
footer {
    visibility: hidden;
}

h1, h2, h3, h4, h5 {
    color: #38294b !important;
}

p {
    color: #766780;
}

.brand-title {
    color: #553879;
    font-size: 1.34rem;
    font-weight: 900;
    line-height: 1.05;
}

.brand-sub {
    color: #9889a3;
    font-size: .71rem;
    margin-top: 4px;
}

.nav-divider {
    height: 1px;
    background: #e7dcf3;
    margin: 12px 0 24px;
}

.status-pill {
    text-align: center;
    padding: 8px 11px;
    border-radius: 999px;
    background: #eee4ff;
    border: 1px solid #dfcdf5;
    color: #70489f;
    font-size: .70rem;
    font-weight: 850;
}

.stButton > button,
.stLinkButton > a {
    min-height: 45px !important;
    border-radius: 13px !important;
    border: 1px solid #dcccf0 !important;
    background: rgba(255,255,255,.94) !important;
    color: #67448e !important;
    font-weight: 800 !important;
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease !important;
}

.stButton > button:hover,
.stLinkButton > a:hover {
    transform: translateY(-2px);
    border-color: #b89bd9 !important;
    box-shadow: 0 9px 23px rgba(94,63,133,.11) !important;
}

.hero {
    text-align: center;
    padding: 43px 30px 35px;
    margin-bottom: 25px;
    border-radius: 31px;
    background: linear-gradient(135deg, #d8c2ff 0%, #e8d8ff 50%, #faf7ff 100%);
    border: 1px solid #d3beed;
    box-shadow: 0 21px 53px rgba(98,67,139,.12);
}

.hero-badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(255,255,255,.80);
    border: 1px solid #dcc9f3;
    color: #70469e;
    font-size: .73rem;
    font-weight: 900;
    letter-spacing: .45px;
}

.hero-title {
    margin-top: 20px;
    color: #302440;
    font-size: clamp(2.8rem, 6vw, 5.2rem);
    line-height: .97;
    font-weight: 900;
    letter-spacing: -2.8px;
}

.hero-title span {
    color: #8557b6;
}

.hero-description {
    max-width: 760px;
    margin: 18px auto 0;
    color: #665474;
    font-size: 1.02rem;
    line-height: 1.72;
}

.hero-note {
    margin-top: 13px;
    color: #796684;
    font-size: .86rem;
    font-weight: 650;
}

.stat-card {
    text-align: center;
    padding: 17px 8px;
    border-radius: 18px;
    background: rgba(255,255,255,.90);
    border: 1px solid #e2d6ef;
}

.stat-number {
    color: #5a3d80;
    font-size: 1.43rem;
    font-weight: 900;
}

.stat-label {
    margin-top: 4px;
    color: #8d7f98;
    font-size: .65rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .4px;
}

.section-title {
    margin-top: 34px;
    color: #49355e;
    font-size: 1.76rem;
    font-weight: 900;
}

.section-subtitle {
    color: #81718c;
    font-size: .90rem;
    margin-bottom: 17px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #e1d5ef !important;
    border-radius: 22px !important;
    background: rgba(255,255,255,.92);
}

label {
    color: #5d486e !important;
    font-weight: 750 !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background: #fdfbff !important;
    border: 1px solid #d9caeb !important;
    border-radius: 12px !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="select"] span {
    color: #3e314e !important;
}

.result-banner {
    padding: 20px 22px;
    margin-top: 30px;
    border-radius: 21px;
    background: linear-gradient(135deg, #eee2ff, #faf8ff);
    border: 1px solid #d9c6ef;
}

.result-title {
    color: #583c7c;
    font-size: 1.5rem;
    font-weight: 900;
}

.result-sub {
    color: #7a6b84;
    font-size: .83rem;
    margin-top: 3px;
}

.ai-panel {
    padding: 22px;
    margin-top: 17px;
    border-radius: 23px;
    background: linear-gradient(135deg, #eadcff, #faf7ff);
    border: 1px solid #d6c1ee;
}

.ai-title {
    color: #563b7c;
    font-size: 1.26rem;
    font-weight: 900;
}

.ai-sub {
    color: #927f9f;
    font-size: .74rem;
}

.gemini-panel {
    padding: 25px;
    margin-top: 18px;
    border-radius: 24px;
    background: linear-gradient(135deg, #36214d, #5a3679);
    color: white;
    box-shadow: 0 15px 40px rgba(53,31,75,.18);
}

.gemini-panel h3 {
    color: white !important;
    margin: 10px 0 7px;
}

.gemini-panel p {
    color: #f3eafb !important;
}

.gemini-chip {
    display: inline-block;
    padding: 7px 11px;
    border-radius: 999px;
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.18);
    color: #f8eaff;
    font-size: .68rem;
    font-weight: 900;
    letter-spacing: .6px;
}

.gemini-error {
    padding: 16px;
    margin-top: 16px;
    border-radius: 16px;
    background: #fff4f8;
    border: 1px solid #efd5e2;
    color: #765568;
}

.pick-badge {
    display: inline-block;
    padding: 7px 11px;
    border-radius: 999px;
    background: #dfcaff;
    color: #70459b;
    font-size: .69rem;
    font-weight: 950;
    letter-spacing: .7px;
}

.pick-name {
    color: #433054;
    font-size: 1.70rem;
    font-weight: 950;
    line-height: 1.18;
    margin-top: 9px;
}

.pick-price {
    color: #704a98;
    font-size: 1.35rem;
    font-weight: 900;
}

.pick-score {
    color: #684191;
    font-size: 2.6rem;
    font-weight: 950;
}

.label {
    color: #95849f;
    font-size: .67rem;
    font-weight: 850;
    text-transform: uppercase;
    letter-spacing: .6px;
}

.why-box {
    padding: 15px;
    margin-top: 15px;
    border-radius: 15px;
    background: #ffffff;
    border: 1px solid #dfd1ee;
    color: #62506e;
    line-height: 1.55;
}

.personal-box {
    padding: 15px;
    margin-top: 12px;
    border-radius: 15px;
    background: #effaf3;
    border: 1px solid #cbe8d5;
    color: #50705c;
    line-height: 1.55;
}

.warning-box {
    padding: 15px;
    margin-top: 15px;
    border-radius: 15px;
    background: #fff4f9;
    border: 1px solid #efd8e5;
    color: #765568;
    line-height: 1.55;
}

.alt-title {
    color: #4b365f;
    font-size: 1.14rem;
    font-weight: 900;
}

.alt-meta {
    color: #94829e;
    font-size: .76rem;
}

.feature-card {
    min-height: 170px;
    padding: 21px;
    border-radius: 20px;
    background: rgba(255,255,255,.91);
    border: 1px solid #e1d5ef;
    box-shadow: 0 8px 23px rgba(87,61,120,.05);
}

.feature-icon {
    font-size: 1.75rem;
}

.feature-title {
    margin-top: 9px;
    color: #4e3963;
    font-size: 1rem;
    font-weight: 850;
}

.feature-text {
    margin-top: 6px;
    color: #776783;
    font-size: .81rem;
    line-height: 1.55;
}

.footer {
    margin-top: 54px;
    padding-top: 20px;
    text-align: center;
    color: #93859f;
    font-size: .76rem;
}

.footer strong {
    color: #704b95;
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# NAVBAR
# ============================================================

brand, home, discover, saved, history, how, status = st.columns(
    [2.5, .7, .9, .85, .85, 1.05, 1.15]
)

with brand:
    st.markdown(
        '<div class="brand-title">🎁 GiftBro AI</div>'
        '<div class="brand-sub">Smarter gifts. Less panic.</div>',
        unsafe_allow_html=True,
    )

with home:
    if st.button("Home", key="nav_home", use_container_width=True):
        go_to("home")

with discover:
    if st.button("Discover", key="nav_discover", use_container_width=True):
        go_to("discover")

with saved:
    if st.button("❤️ Saved", key="nav_saved", use_container_width=True):
        go_to("saved")

with history:
    if st.button("🕘 History", key="nav_history", use_container_width=True):
        go_to("history")

with how:
    if st.button("How it works", key="nav_how", use_container_width=True):
        go_to("how")

with status:
    st.markdown(
        '<div class="status-pill">✨ Smart gifting</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="nav-divider"></div>',
    unsafe_allow_html=True,
)


# ============================================================
# HOME
# ============================================================

if st.session_state.page == "home":

    st.markdown(
        """
<div class="hero">
<div class="hero-badge">✨ PERSONALIZED GIFT DISCOVERY • SYSTEM READY</div>
<div class="hero-title">Stop guessing gifts.<br><span>Find the perfect one.</span> 🎁</div>
<div class="hero-description">
Tell GiftBro who you're buying for, what they love, the occasion,
your budget and the kind of gift you want. GiftBro ranks the candidates.
Gemini can then add the human touch.
</div>
<div class="hero-note">😎 Your slightly overconfident best friend for gift decisions.</div>
</div>
""",
        unsafe_allow_html=True,
    )

    s1, s2, s3, s4 = st.columns(4)

    for col, value, label in [
        (s1, "2,000+", "Gift candidates"),
        (s2, "ML + AI", "Hybrid intelligence"),
        (s3, "9", "Ranking signals"),
        (s4, "❤️ + 🛍️", "Save & shop"),
    ]:
        with col:
            st.markdown(
                f'<div class="stat-card"><div class="stat-number">{value}</div>'
                f'<div class="stat-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="section-title">🎯 Ready when you are</div>'
        '<div class="section-subtitle">Build a gift profile in under a minute.</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([2, 1])

    with c1:
        if st.button(
            "🎁 Start finding a gift →",
            key="start_gift",
            use_container_width=True,
            type="primary",
        ):
            go_to("discover")

    with c2:
        if st.button(
            "⚡ Try the demo",
            key="home_demo",
            use_container_width=True,
        ):
            create_search(
                recipient="Girlfriend",
                age=21,
                relationship="Partner",
                occasion="Birthday",
                interests="books photography skincare",
                personality=["Creative", "Sentimental"],
                budget=3000,
                gift_style="Sentimental",
                personalization_level="High",
                avoid_items="mugs",
                recommendation_mode="Most Personal",
                occasion_importance="Important",
            )
            go_to("results")

    st.write("")

    features = [
        ("💡", "Tell GiftBro", "Describe the person, occasion, interests, personality and budget."),
        ("🧠", "Get ranked matches", "TF-IDF, cosine similarity and contextual signals rank the catalogue."),
        ("✨", "Let Gemini cook", "Gemini enriches the ranked candidates only when you ask for it."),
    ]

    cols = st.columns(3)

    for col, (icon, title, text) in zip(cols, features):
        with col:
            st.markdown(
                f'<div class="feature-card"><div class="feature-icon">{icon}</div>'
                f'<div class="feature-title">{title}</div>'
                f'<div class="feature-text">{text}</div></div>',
                unsafe_allow_html=True,
            )


# ============================================================
# DISCOVER
# ============================================================

elif st.session_state.page == "discover":

    st.markdown(
        """
<div class="hero">
<div class="hero-badge">🎯 GIFT DISCOVERY WORKSPACE</div>
<div class="hero-title">Tell me about <span>them.</span></div>
<div class="hero-description">
Give me the clues. GiftBro handles the ranking. Gemini is optional.
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.container(border=True):

        st.subheader("👤 Who are we buying for?")

        c1, c2, c3 = st.columns(3)

        with c1:
            recipient = st.text_input(
                "Name / role",
                placeholder="e.g. Girlfriend, Dad, Best Friend",
                key="recipient_field",
            )

        with c2:
            age = st.number_input(
                "Age",
                min_value=5,
                max_value=100,
                value=21,
                key="age_field",
            )

        with c3:
            relationship = st.selectbox(
                "Relationship",
                [
                    "Partner",
                    "Best Friend",
                    "Friend",
                    "Sibling",
                    "Parent",
                    "Family",
                    "Colleague",
                    "Classmate",
                    "Mentor",
                ],
                key="relationship_field",
            )

        st.divider()

        st.subheader("✨ Occasion & personality")

        c1, c2 = st.columns(2)

        with c1:
            occasion = st.selectbox(
                "Occasion",
                [
                    "Birthday",
                    "Anniversary",
                    "Valentines Day",
                    "Graduation",
                    "Housewarming",
                    "Farewell",
                    "Christmas",
                    "Friendship Day",
                    "Wedding",
                    "Promotion",
                    "Thank You",
                    "Just Because",
                ],
                key="occasion_field",
            )

        with c2:
            interests = st.text_input(
                "Interests",
                placeholder="e.g. books, photography, gaming, skincare",
                key="interests_field",
            )

        personality = st.multiselect(
            "Personality",
            [
                "Sentimental",
                "Creative",
                "Romantic",
                "Practical",
                "Minimalist",
                "Adventurous",
                "Introverted",
                "Extroverted",
                "Stylish",
                "Intellectual",
                "Funny",
                "Techie",
                "Classic",
                "Trendy",
            ],
            default=["Creative", "Sentimental"],
            key="personality_field",
        )

        st.divider()

        st.subheader("🎨 Gift preferences")

        p1, p2 = st.columns(2)

        with p1:
            gift_style = st.selectbox(
                "Gift style",
                [
                    "Surprise Me",
                    "Practical",
                    "Sentimental",
                    "Fun",
                    "Luxury",
                    "Creative",
                ],
                key="gift_style_field",
            )

        with p2:
            personalization_level = st.selectbox(
                "Personalization level",
                ["Low", "Medium", "High"],
                index=1,
                key="personalization_field",
            )

        avoid_items = st.text_input(
            "Anything to avoid?",
            placeholder="e.g. mugs, fragrances, skincare",
            key="avoid_field",
        )

        st.divider()

        st.subheader("💰 Budget")

        budget = st.slider(
            "Maximum budget",
            min_value=300,
            max_value=20000,
            value=3000,
            step=100,
            key="budget_field",
        )

        st.caption(f"Maximum spend: ₹{budget:,}")

        st.divider()

        st.subheader("🎯 Recommendation strategy")

        r1, r2 = st.columns(2)

        with r1:
            recommendation_mode = st.selectbox(
                "Optimize for",
                [
                    "Best Overall",
                    "Best Value",
                    "Most Personal",
                    "Most Unique",
                ],
                key="recommendation_mode_field",
            )

        with r2:
            occasion_importance = st.selectbox(
                "Occasion importance",
                [
                    "Casual",
                    "Important",
                    "Major Milestone",
                ],
                key="occasion_importance_field",
            )

        st.caption(
            "These preferences shape the ranking before Gemini is asked to personalize it."
        )

        st.write("")

        b1, b2 = st.columns([3, 1])

        with b1:
            generate = st.button(
                "🎁 FIND MY PERFECT GIFT →",
                key="discover_generate",
                use_container_width=True,
                type="primary",
            )

        with b2:
            demo = st.button(
                "⚡ Demo",
                key="discover_demo",
                use_container_width=True,
            )

    if demo:
        create_search(
            recipient="Girlfriend",
            age=21,
            relationship="Partner",
            occasion="Birthday",
            interests="books photography skincare",
            personality=["Creative", "Sentimental"],
            budget=3000,
            gift_style="Sentimental",
            personalization_level="High",
            avoid_items="mugs",
            recommendation_mode="Most Personal",
            occasion_importance="Important",
        )
        go_to("results")

    if generate:

        if not recipient.strip():
            st.warning("Bro, who are we buying for? 😭")
            st.stop()

        if not interests.strip():
            st.warning("Give me at least a couple of interests.")
            st.stop()

        with st.spinner("🎁 Ranking gifts..."):
            create_search(
                recipient=recipient,
                age=age,
                relationship=relationship,
                occasion=occasion,
                interests=interests,
                personality=personality,
                budget=budget,
                gift_style=gift_style,
                personalization_level=personalization_level,
                avoid_items=avoid_items,
                recommendation_mode=recommendation_mode,
                occasion_importance=occasion_importance,
            )

        go_to("results")


# ============================================================
# RESULTS
# ============================================================

elif st.session_state.page == "results":

    recommendations = st.session_state.get("recommendations")
    advice = st.session_state.get("advice")
    gemini = st.session_state.get("gemini_advice")
    profile = st.session_state.get("profile")

    if recommendations is None or advice is None or profile is None:
        go_to("discover")

    st.markdown(
        """
<div class="hero">
<div class="hero-badge">✨ ANALYSIS COMPLETE</div>
<div class="hero-title">Your shortlist is <span>ready.</span></div>
<div class="hero-description">
GiftBro ranked the catalogue using your profile and recommendation strategy.
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="result-banner">
<div class="result-title">✨ GiftBro found some serious contenders.</div>
<div class="result-sub">
Ranked using preferences, context, budget and recommendation strategy.
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.caption(
        " · ".join(
            [
                str(profile.get("relationship", "")),
                str(profile.get("occasion", "")),
                str(profile.get("gift_style", "")),
                str(profile.get("recommendation_mode", "")),
            ]
        )
    )

    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    if gemini is None:

        st.markdown(
            """
<div class="gemini-panel">
<span class="gemini-chip">✨ OPTIONAL AI ENRICHMENT</span>
<h3>Let Gemini cook the final recommendation.</h3>
<p>
The ML engine has already ranked real catalogue candidates.
Gemini can now turn those candidates into personalized advice.
</p>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button(
            "✨ Ask Gemini to personalize this →",
            key="results_ask_gemini",
            use_container_width=True,
            type="primary",
        ):
            ask_gemini()

    elif gemini.get("status") == "ok":

        st.markdown(
            """
<div class="gemini-panel">
<span class="gemini-chip">✨ GEMINI PERSONALIZATION</span>
<h3>The ML engine found the candidates. Gemini cooked the final take.</h3>
</div>
""",
            unsafe_allow_html=True,
        )

        if gemini.get("headline"):
            st.markdown(
                f"### {gemini['headline']}"
            )

        g1, g2 = st.columns(2)

        with g1:
            st.markdown("### Why it fits")
            st.write(gemini.get("why_best", ""))

            st.markdown("### Personalization idea")
            st.write(gemini.get("personalization_idea", ""))

        with g2:
            st.markdown("### How to present it")
            st.write(gemini.get("presentation_idea", ""))

            st.markdown("### Message to include")
            st.write(gemini.get("message_to_include", ""))

        if gemini.get("decision_note"):
            st.info(gemini["decision_note"])

        if gemini.get("best_gift"):
            ml_top = ""
            if recommendations is not None and not recommendations.empty:
                ml_top = str(recommendations.iloc[0]["name"])

            if str(gemini["best_gift"]) == ml_top:
                st.caption(
                    f"✅ Gemini agrees with GiftBro's ML #1: **{gemini['best_gift']}**"
                )
            else:
                st.caption(
                    f"✨ Gemini selected another ranked candidate: **{gemini['best_gift']}**"
                )

        with st.expander("🧭 How this was decided"):
            st.markdown(
                """
**1. Profile**
→ recipient, relationship, occasion, interests, personality, budget and preferences

**2. ML ranking**
→ TF-IDF + cosine similarity + contextual signals

**3. Catalogue shortlist**
→ only ranked catalogue candidates move forward

**4. Gemini**
→ personalization and presentation, without inventing products

**5. Action**
→ save, shop, inspect, or regenerate
"""
            )

        if st.button(
            "↻ Re-cook with Gemini",
            key="recook_gemini",
            use_container_width=True,
        ):
            ask_gemini()

    else:

        st.markdown(
            f"""
<div class="gemini-error">
<strong>Gemini personalization unavailable.</strong><br>
{gemini.get("error", "Unknown Gemini error.")}
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button(
            "↻ Try Gemini again",
            key="retry_gemini",
            use_container_width=True,
        ):
            st.session_state.gemini_advice = None
            st.rerun()

    # --------------------------------------------------------
    # GIFTBRO AI
    # --------------------------------------------------------

    with st.container(border=True):

        st.markdown(
            '<div class="ai-title">😎 GiftBro AI</div>'
            '<div class="ai-sub">Your slightly overconfident gift consultant.</div>',
            unsafe_allow_html=True,
        )

        st.info(advice["opening"])

        best = advice.get("best")

        if best:

            st.markdown(
                '<span class="pick-badge">🏆 GIFTBRO\'S #1 PICK</span>',
                unsafe_allow_html=True,
            )

            p1, p2, p3 = st.columns([2.35, 1, 1])

            with p1:
                st.markdown(
                    f'<div class="pick-name">🎁 {best["name"]}</div>',
                    unsafe_allow_html=True,
                )
                st.caption(
                    f'{best["category"]} · {best["verdict"]}'
                )

            with p2:
                st.markdown(
                    '<div class="label">PRICE</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="pick-price">₹{best["price"]:,}</div>',
                    unsafe_allow_html=True,
                )

            with p3:
                st.markdown(
                    '<div class="label">MATCH</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="pick-score">{best["score"]:.0f}%</div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                f'<div class="why-box">✨ <b>Why this one?</b><br>{best["why"]}</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div class="personal-box">💡 <b>Personal touch</b><br>{best["personalization"]}</div>',
                unsafe_allow_html=True,
            )

            b1, b2, b3 = st.columns(3)

            with b1:
                if favorite_exists(best["name"]):
                    st.success("❤️ Saved")
                elif st.button(
                    "❤️ Save gift",
                    key="save_best",
                    use_container_width=True,
                ):
                    save_favorite(
                        gift_name=best["name"],
                        category=best["category"],
                        price=best["price"],
                        match_score=best["score"],
                        description=best["description"],
                        personalization=best["personalization"],
                    )
                    st.toast("❤️ Saved to Favorites!")
                    st.rerun()

            with b2:
                st.link_button(
                    "🛍️ Shop this gift",
                    shop_url(best["name"], "amazon"),
                    use_container_width=True,
                )

            with b3:
                if st.button(
                    "🔍 View details",
                    key="best_details",
                    use_container_width=True,
                ):
                    st.session_state.selected_gift = best
                    go_to("detail")

            st.markdown(
                f"### 🏆 My pick\n{advice['pick']}"
            )

    st.markdown(
        f'<div class="warning-box">🚨 <b>Bro, don\'t do this</b><br>{advice["warning"]}</div>',
        unsafe_allow_html=True,
    )

    alternatives = advice.get("alternatives", [])

    if alternatives:

        st.markdown(
            '<div class="section-title">💜 Strong alternatives</div>'
            '<div class="section-subtitle">Excellent backup choices.</div>',
            unsafe_allow_html=True,
        )

        cols = st.columns(2)

        for index, gift in enumerate(alternatives[:2]):

            with cols[index]:

                with st.container(border=True):

                    st.markdown(
                        f'<div class="alt-title">{["💜", "✨"][index]} {gift["name"]}</div>',
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        f'<div class="alt-meta">#{gift["rank"]} · {gift["category"]} · {gift["verdict"]}</div>',
                        unsafe_allow_html=True,
                    )

                    c1, c2 = st.columns(2)

                    with c1:
                        st.metric("Price", money(gift["price"]))

                    with c2:
                        st.metric("Match", f'{gift["score"]:.0f}%')

                    st.write(gift["description"])

                    st.success(
                        "💡 " + gift["personalization"]
                    )

                    x1, x2 = st.columns(2)

                    with x1:
                        st.link_button(
                            "🛍️ Shop",
                            shop_url(gift["name"], "google"),
                            use_container_width=True,
                        )

                    with x2:
                        if st.button(
                            "🔍 Details",
                            key=f"alt_details_{index}",
                            use_container_width=True,
                        ):
                            st.session_state.selected_gift = gift
                            go_to("detail")

    st.write("")

    c1, c2 = st.columns(2)

    with c1:
        if st.button(
            "🔄 Regenerate recommendations",
            key="regenerate_results",
            use_container_width=True,
        ):

            previous = []

            if recommendations is not None and not recommendations.empty:
                previous = (
                    recommendations["name"]
                    .astype(str)
                    .tolist()
                )

            with st.spinner("🔄 Finding a fresh set of gifts..."):
                create_search(
                    recipient=profile["recipient"],
                    age=profile["age"],
                    relationship=profile["relationship"],
                    occasion=profile["occasion"],
                    interests=profile["interests"],
                    personality=profile["personality"],
                    budget=profile["budget"],
                    gift_style=profile["gift_style"],
                    personalization_level=profile["personalization_level"],
                    avoid_items=profile["avoid_items"],
                    recommendation_mode=profile["recommendation_mode"],
                    occasion_importance=profile["occasion_importance"],
                    exclude_names=previous,
                )

            st.session_state.generation_number += 1
            st.rerun()

    with c2:
        if st.button(
            "🎯 Start a new search",
            key="new_search_results",
            use_container_width=True,
        ):

            st.session_state.recommendations = None
            st.session_state.advice = None
            st.session_state.gemini_advice = None
            st.session_state.profile = None
            st.session_state.selected_gift = None
            st.session_state.generation_number = 0

            go_to("discover")


# ============================================================
# DETAIL
# ============================================================

elif st.session_state.page == "detail":

    gift = st.session_state.get("selected_gift")
    profile = st.session_state.get("profile") or {}
    gemini = st.session_state.get("gemini_advice")
    recommendations = st.session_state.get("recommendations")

    if not gift:
        go_to("results")

    st.markdown(
        """
<div class="hero">
<div class="hero-badge">🎁 GIFT DETAIL</div>
<div class="hero-title">Let's inspect this <span>choice.</span></div>
<div class="hero-description">
See the recommendation signals behind this candidate.
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.container(border=True):

        st.markdown(
            '<span class="pick-badge">✨ RECOMMENDED CANDIDATE</span>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="pick-name">🎁 {gift["name"]}</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            f'{gift["category"]} · {gift["verdict"]}'
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Price",
                money(gift["price"]),
            )

        with c2:
            st.metric(
                "Overall match",
                f'{safe_number(gift.get("score")):.0f}%',
            )

        with c3:
            budget_fit = calculate_budget_fit(
                gift.get("price"),
                profile.get("budget", 0),
            )
            st.metric(
                "Budget fit",
                f"{budget_fit * 100:.0f}%",
            )

        st.divider()

        st.subheader("✨ Why this gift?")
        st.write(gift["description"])

        st.markdown(
            f'<div class="why-box">✨ <b>Recommendation reason</b><br>{gift["why"]}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="personal-box">💡 <b>Personal touch</b><br>{gift["personalization"]}</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        st.subheader("📊 Match breakdown")

        for label, key in [
            ("Semantic similarity", "cosine_score"),
            ("Interests", "interest_match"),
            ("Occasion", "occasion_match"),
            ("Relationship", "relationship_match"),
            ("Personality", "personality_match"),
            ("Gift style", "style_match"),
            ("Personalization", "personalization_match"),
            ("Budget", None),
        ]:

            if key is None:
                value = calculate_budget_fit(
                    gift.get("price"),
                    profile.get("budget", 0),
                )
            else:
                value = min(
                    max(
                        safe_number(gift.get(key)),
                        0.0,
                    ),
                    1.0,
                )

            percentage = value * 100

            st.write(
                f"**{label}** · {percentage:.0f}%"
            )

            st.progress(
                int(percentage)
            )

        if gift.get("score_breakdown"):

            with st.expander("See scoring details"):
                st.code(
                    str(gift["score_breakdown"]),
                    language="text",
                )

        st.divider()

        # ----------------------------------------------------
        # GEMINI ON DETAILS
        # ----------------------------------------------------

        if gemini is None:

            st.markdown(
                """
<div class="gemini-panel">
<span class="gemini-chip">✨ OPTIONAL AI ENRICHMENT</span>
<h3>Want Gemini's take on this gift?</h3>
<p>
Gemini will personalize this recommendation using the ranked
catalogue candidates and your original gift profile.
</p>
</div>
""",
                unsafe_allow_html=True,
            )

            if st.button(
                "✨ Ask Gemini to personalize this →",
                key="detail_ask_gemini",
                use_container_width=True,
                type="primary",
            ):
                ask_gemini()

        elif gemini.get("status") == "ok":

            st.markdown(
                """
<div class="gemini-panel">
<span class="gemini-chip">✨ GEMINI PERSONALIZATION</span>
<h3>Gemini's take on the gift</h3>
</div>
""",
                unsafe_allow_html=True,
            )

            if gemini.get("headline"):
                st.markdown(
                    f"### {gemini['headline']}"
                )

            d1, d2 = st.columns(2)

            with d1:
                st.markdown("### Why it fits")
                st.write(gemini.get("why_best", ""))

                st.markdown("### Personalization idea")
                st.write(
                    gemini.get(
                        "personalization_idea",
                        "",
                    )
                )

            with d2:
                st.markdown("### How to present it")
                st.write(
                    gemini.get(
                        "presentation_idea",
                        "",
                    )
                )

                st.markdown("### Message to include")
                st.write(
                    gemini.get(
                        "message_to_include",
                        "",
                    )
                )

            if gemini.get("decision_note"):
                st.info(
                    gemini["decision_note"]
                )

            if st.button(
                "↻ Re-cook with Gemini",
                key="detail_recook_gemini",
                use_container_width=True,
            ):
                ask_gemini()

        else:

            st.markdown(
                f"""
<div class="gemini-error">
<strong>Gemini personalization unavailable.</strong><br>
{gemini.get("error", "Unknown Gemini error.")}
</div>
""",
                unsafe_allow_html=True,
            )

            if st.button(
                "↻ Try Gemini again",
                key="detail_retry_gemini",
                use_container_width=True,
            ):
                st.session_state.gemini_advice = None
                st.rerun()

        st.divider()

        b1, b2, b3 = st.columns(3)

        with b1:

            if favorite_exists(gift["name"]):
                st.success("❤️ Saved")

            elif st.button(
                "❤️ Save gift",
                key="detail_save",
                use_container_width=True,
            ):

                save_favorite(
                    gift_name=gift["name"],
                    category=gift["category"],
                    price=gift["price"],
                    match_score=gift["score"],
                    description=gift["description"],
                    personalization=gift["personalization"],
                )

                st.toast("❤️ Saved to Favorites!")
                st.rerun()

        with b2:

            st.link_button(
                "🛍️ Shop on Amazon",
                shop_url(gift["name"], "amazon"),
                use_container_width=True,
            )

        with b3:

            st.link_button(
                "🔎 Compare online",
                shop_url(gift["name"], "google"),
                use_container_width=True,
            )

    if st.button(
        "← Back to results",
        key="back_results",
        use_container_width=True,
    ):
        go_to("results")


# ============================================================
# SAVED
# ============================================================

elif st.session_state.page == "saved":

    st.markdown(
        """
<div class="hero">
<div class="hero-badge">❤️ SAVED GIFTS</div>
<div class="hero-title">Your shortlist.<br><span>Saved for later.</span></div>
<div class="hero-description">
Keep your strongest gift ideas in one place.
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    favorites = get_favorites()

    if not favorites:

        st.info(
            "No saved gifts yet. Go find something dangerously thoughtful. 😎"
        )

        if st.button(
            "🎁 Find a gift",
            key="empty_saved",
            use_container_width=True,
        ):
            go_to("discover")

    else:

        st.markdown(
            f'<div class="section-title">❤️ {len(favorites)} saved gift'
            f'{"s" if len(favorites) != 1 else ""}</div>',
            unsafe_allow_html=True,
        )

        for favorite in favorites:

            with st.container(border=True):

                c1, c2, c3 = st.columns([2.5, 1, 1])

                with c1:
                    st.subheader(
                        f'🎁 {favorite["gift_name"]}'
                    )
                    st.caption(
                        favorite["category"]
                    )
                    st.write(
                        favorite["description"]
                    )

                with c2:
                    st.metric(
                        "Price",
                        money(favorite["price"]),
                    )

                with c3:
                    st.metric(
                        "Match",
                        f'{safe_number(favorite["match_score"]):.0f}%',
                    )

                st.success(
                    "💡 " + favorite["personalization"]
                )

                b1, b2, b3 = st.columns(3)

                with b1:
                    st.link_button(
                        "🛍️ Amazon",
                        shop_url(
                            favorite["gift_name"],
                            "amazon",
                        ),
                        use_container_width=True,
                    )

                with b2:
                    st.link_button(
                        "🔎 Search",
                        shop_url(
                            favorite["gift_name"],
                            "google",
                        ),
                        use_container_width=True,
                    )

                with b3:
                    if st.button(
                        "🗑️ Remove",
                        key=f"delete_saved_{favorite['id']}",
                        use_container_width=True,
                    ):
                        delete_favorite(
                            favorite["id"]
                        )
                        st.toast("Gift removed.")
                        st.rerun()


# ============================================================
# HISTORY
# ============================================================

elif st.session_state.page == "history":

    st.markdown(
        """
<div class="hero">
<div class="hero-badge">🕘 SEARCH HISTORY</div>
<div class="hero-title">Your gift-search<br><span>trail.</span></div>
<div class="hero-description">
Every recommendation session is stored locally with SQLite.
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    history = get_history(30)

    if not history:

        st.info("No recommendation history yet.")

    else:

        st.markdown(
            f'<div class="section-title">🕘 {len(history)} recent searches</div>',
            unsafe_allow_html=True,
        )

        for record in history:

            with st.container(border=True):

                st.subheader(
                    f'🎁 {record["recipient"]}'
                )

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    st.caption("OCCASION")
                    st.write(record["occasion"])

                with c2:
                    st.caption("RELATIONSHIP")
                    st.write(record["relationship"])

                with c3:
                    st.caption("BUDGET")
                    st.write(money(record["budget"]))

                with c4:
                    st.caption("DATE")
                    st.write(
                        str(record["created_at"])[:10]
                    )

                st.caption(
                    "Interests: "
                    + str(record["interests"])
                )

                st.write(
                    "**Recommended:** "
                    + str(record["selected_gifts"])
                )


# ============================================================
# HOW IT WORKS
# ============================================================

elif st.session_state.page == "how":

    st.markdown(
        """
<div class="hero">
<div class="hero-badge">🧠 UNDER THE HOOD</div>
<div class="hero-title">A gift recommender<br><span>with a brain.</span></div>
<div class="hero-description">
GiftBro combines machine-learning ranking with optional Gemini personalization.
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    features = [
        (
            "📚",
            "Gift catalogue",
            "Structured gift data including price, category, occasion, relationship, interests and personality.",
        ),
        (
            "🔤",
            "TF-IDF",
            "Turns catalogue and profile text into numerical feature vectors.",
        ),
        (
            "🎯",
            "Cosine similarity",
            "Measures semantic similarity between the user profile and catalogue entries.",
        ),
        (
            "❤️",
            "Context matching",
            "Explicitly scores interests, occasion, relationship and personality.",
        ),
        (
            "🎨",
            "Preference signals",
            "Gift style, personalization level and recommendation mode affect ranking.",
        ),
        (
            "💰",
            "Budget fit",
            "Keeps recommendations aligned with the user's spending limit.",
        ),
        (
            "✨",
            "Gemini",
            "Adds personalized explanations, presentation ideas and messages after ranking.",
        ),
        (
            "💾",
            "SQLite",
            "Persists favorites and recommendation history.",
        ),
    ]

    row1 = st.columns(4)
    row2 = st.columns(4)

    for col, item in zip(row1, features[:4]):
        icon, title, text = item
        with col:
            st.markdown(
                f'<div class="feature-card"><div class="feature-icon">{icon}</div>'
                f'<div class="feature-title">{title}</div>'
                f'<div class="feature-text">{text}</div></div>',
                unsafe_allow_html=True,
            )

    for col, item in zip(row2, features[4:]):
        icon, title, text = item
        with col:
            st.markdown(
                f'<div class="feature-card"><div class="feature-icon">{icon}</div>'
                f'<div class="feature-title">{title}</div>'
                f'<div class="feature-text">{text}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")

    with st.container(border=True):

        st.subheader("🏗️ GiftBro architecture")

        st.code(
            """
User profile
     ↓
Candidate filtering
     ↓
TF-IDF + cosine similarity
     +
Contextual signals
     +
Gift preferences
     +
Budget
     ↓
Hybrid ranking
     ↓
Real catalogue shortlist
     ↓
Optional Gemini enrichment
     ↓
Final gifting experience
     ├── Save
     ├── Shop
     ├── Details
     └── Regenerate
     ↓
SQLite
  ├── Favorites
  └── History
""",
            language="text",
        )

        st.subheader("🔍 Explainability")

        st.write(
            "GiftBro exposes the recommendation signals instead of hiding "
            "the ranking behind a black box. Gemini is a separate enrichment "
            "layer and receives only ranked catalogue candidates."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">
🎁 <strong>GiftBro AI</strong><br>
Personalized gifting powered by Python + machine learning + Gemini.
</div>
""",
    unsafe_allow_html=True,
)
