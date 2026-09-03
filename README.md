# GiftBro AI 🎁

GiftBro AI is a personalized gift recommendation system that combines
machine learning, contextual ranking, and generative AI to help users
find better gifts for specific people and occasions.

Instead of simply generating gift ideas, GiftBro first ranks real catalogue
items using a hybrid recommendation system and then optionally uses Gemini
to add a personalized explanation.

---

## ✨ What GiftBro Does

A user provides information about the recipient:

- Name / role
- Age
- Relationship
- Occasion
- Interests
- Personality
- Gift style
- Personalization level
- Budget
- Things to avoid
- Recommendation preference

GiftBro then:

1. Filters suitable gift candidates.
2. Calculates semantic similarity using TF-IDF.
3. Uses cosine similarity to compare the recipient profile with gift data.
4. Combines contextual signals such as relationship, occasion, personality,
   interests, and budget.
5. Produces a ranked shortlist.
6. Optionally sends the ranked candidates to Gemini for deeper personalization.
7. Allows users to save gifts and view recommendation history.

---

## 🧠 Recommendation Architecture

```text
                    User Profile
                         │
                         ▼
                 Candidate Filtering
                         │
                         ▼
              ┌──────────────────────┐
              │   Recommendation     │
              │       Engine         │
              └──────────────────────┘
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
        TF-IDF Vectorization    Context Signals
             │                       │
             └───────────┬───────────┘
                         ▼
                  Cosine Similarity
                         │
                         ▼
                  Hybrid Ranking
                         │
                         ▼
                Top Gift Candidates
                         │
                         ▼
               Fast Results Display
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        Save / Details       Optional Gemini
                                    │
                                    ▼
                           Personalized Advice