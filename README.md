# 🎁 GiftBro AI

GiftBro AI is a personalized gift recommendation system that combines machine learning, contextual matching, persistent storage, and a conversational recommendation layer.

## Features

- Personalized gift recommendations
- TF-IDF based text representation
- Cosine similarity
- Occasion matching
- Relationship matching
- Interest matching
- Personality matching
- Budget-aware ranking
- GiftBro conversational personality
- Save favorite gifts
- Recommendation history
- Shopping search links
- FastAPI backend
- Streamlit frontend
- SQLite persistence

## Architecture

User Profile
→ Feature Construction
→ TF-IDF
→ Cosine Similarity
→ Context Matching
→ Budget Filtering
→ Hybrid Ranking
→ GiftBro Coach
→ Recommendation UI

## Tech Stack

- Python
- Pandas
- Scikit-learn
- TF-IDF
- Cosine Similarity
- Streamlit
- FastAPI
- SQLite
- Pydantic

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py