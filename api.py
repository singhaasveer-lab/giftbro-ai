from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from recommender import recommend_gifts
from ai_coach import generate_gift_advice
from database import save_recommendation


app = FastAPI(
    title="GiftBro AI API",
    description=(
        "Personalized gift recommendation API "
        "powered by TF-IDF and cosine similarity."
    ),
    version="1.0.0",
)


class GiftRequest(BaseModel):

    recipient: str = Field(
        min_length=1,
        max_length=100,
    )

    age: int = Field(
        ge=5,
        le=100,
    )

    relationship: str

    occasion: str

    interests: str = Field(
        min_length=1,
        max_length=500,
    )

    personality: List[str]

    budget: int = Field(
        ge=300,
        le=20000,
    )


@app.get("/")
def root():
    return {
        "name": "GiftBro AI",
        "status": "online",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/recommend")
def recommend(request: GiftRequest):

    try:

        personality_text = " ".join(
            request.personality
        )

        if not personality_text:
            personality_text = "Practical"

        recommendations = recommend_gifts(
            occasion=request.occasion,
            relationship=request.relationship,
            interests=request.interests,
            personality=personality_text,
            budget=request.budget,
            top_n=5,
        )

        advice = generate_gift_advice(
            recipient=request.recipient,
            age=request.age,
            relationship=request.relationship,
            occasion=request.occasion,
            interests=request.interests,
            personality=personality_text,
            budget=request.budget,
            recommendations=recommendations,
        )

        save_recommendation(
            recipient=request.recipient,
            age=request.age,
            relationship=request.relationship,
            occasion=request.occasion,
            interests=request.interests,
            personality=personality_text,
            budget=request.budget,
            selected_gifts=", ".join(
                recommendations["name"].tolist()
            ),
        )

        return {
            "coach": advice,
            "recommendations": (
                recommendations
                .to_dict(orient="records")
            ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc