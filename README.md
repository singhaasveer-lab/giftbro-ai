# 🎁 GiftBro AI

**GiftBro AI is a hybrid gift recommendation system that combines machine learning with generative AI to help users find more relevant, personalized gifts.**

Instead of simply asking an AI to invent gift ideas, GiftBro first ranks real catalogue items using a recommendation engine and then optionally uses Gemini to add the human touch.

---

## ✨ What is GiftBro?

Choosing a gift sounds simple until you actually have to choose one.

GiftBro turns that process into a structured recommendation workflow.

The user provides information about the recipient, including:

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
- Recommendation strategy

GiftBro then analyzes that profile against its gift catalogue and produces a ranked shortlist.

Gemini can then take that shortlist and generate personalized advice such as:

- Why the gift fits
- How to personalize it
- How to present it
- A message to include
- A final recommendation note

---

## 🚀 Why GiftBro?

GiftBro combines two different AI approaches in one recommendation pipeline.

**Machine Learning** handles retrieval and ranking.

**Gemini** handles generative personalization.

Instead of asking a language model to invent a gift from scratch, GiftBro first finds relevant candidates from its catalogue and then uses Gemini to explain and personalize those candidates.

```text
User Profile
      ↓
Candidate Filtering
      ↓
ML Ranking
      ↓
Real Catalogue Candidates
      ↓
Gemini Personalization
      ↓
Personalized Recommendation
```

---

# 🛠️ Tech Stack

### 🎨 Frontend

- Streamlit

### ⚙️ Backend & API

- Python
- FastAPI
- Uvicorn

### 🧠 Machine Learning

- Scikit-learn
- TF-IDF Vectorization
- Cosine Similarity
- Hybrid Recommendation Ranking

### 🤖 Generative AI

- Google Gemini
- Gemini API

### 💾 Data & Storage

- Pandas
- SQLite
- CSV

### 🔧 Development

- Python
- python-dotenv

---

# ⭐ Key Features

- 🎁 Personalized gift recommendations
- 🧠 Hybrid ML + Generative AI recommendation pipeline
- 🔎 TF-IDF based catalogue matching
- 📐 Cosine similarity scoring
- ❤️ Relationship-aware recommendations
- 🎉 Occasion-aware recommendations
- 🎨 Personality and interest matching
- 💰 Budget-aware recommendations
- 🚫 Things-to-avoid preferences
- 🏆 Ranked gift shortlist
- ✨ Optional Gemini personalization
- 💾 SQLite-based history and favorites
- 🔄 Regenerate recommendations
- 🔍 Search and explore gift options
- ⚡ FastAPI backend endpoint
- 📱 Streamlit interactive interface

---

# 🧠 Recommendation System

GiftBro does not rely on a single recommendation score.

Instead, it combines multiple signals to determine how well a gift matches a user's profile.

### 1. Candidate Filtering

The system first narrows down the catalogue based on relevant user preferences and constraints.

```text
User Profile
      ↓
Catalogue
      ↓
Candidate Filtering
      ↓
Relevant Gift Candidates
```

### 2. TF-IDF Features

Gift and user-profile information can be represented as text features using TF-IDF.

This helps the recommendation engine understand textual relationships between user interests and gift attributes.

### 3. Cosine Similarity

Cosine similarity is used to measure how closely the user's profile matches available catalogue items.

```text
User Profile Vector
        │
        ▼
   TF-IDF Vector
        │
        ▼
Cosine Similarity
        │
        ▼
Gift Relevance Score
```

### 4. Context Signals

GiftBro also considers contextual information such as:

- Occasion
- Relationship
- Interests
- Personality
- Gift style
- Budget
- Personalization preferences

### 5. Hybrid Ranking

These signals are combined to produce a ranked shortlist of gift candidates.

```text
                 USER PROFILE
                      │
                      ▼
             Candidate Filtering
                      │
                      ▼
           ┌─────────────────────┐
           │ Recommendation      │
           │      Engine         │
           └─────────────────────┘
                      │
             ┌────────┴────────┐
             ▼                 ▼
       TF-IDF Features    Context Signals
             │                 │
             ▼                 ▼
      Cosine Similarity    Occasion Match
                           Relationship Match
                           Interest Match
                           Personality Match
             │                 │
             └────────┬────────┘
                      ▼
                Preference Signals
                      │
                      ▼
                   Budget Fit
                      │
                      ▼
                 Hybrid Ranking
                      │
                      ▼
              Top Gift Candidates
                      │
                      ▼
                  FAST RESULTS
                      │
                      ▼
             Optional Gemini Layer
                      │
                      ▼
             Personalized Gift Advice
```

---

# 🤖 Gemini Personalization

Gemini is used as an optional personalization layer after the recommendation engine has identified relevant gift candidates.

Instead of asking Gemini to generate random gifts, GiftBro provides the recommendation context and allows Gemini to help produce more personalized guidance.

Gemini can help generate:

- Why the gift fits
- How to personalize it
- How to present it
- A message to include
- A final recommendation note

This creates a separation between **recommendation** and **generation**.

```text
Machine Learning
      │
      ▼
Find relevant gifts
      │
      ▼
Rank candidates
      │
      ▼
Gemini
      │
      ▼
Personalized advice
```

---

# 📊 Product Demo

## 🏠 Home

![GiftBro Home](assets/home.png)

---

## 🎯 Build a Gift Profile

![GiftBro Discover](assets/discover.png)

---

## 🎨 Fine-Tune Preferences

![Gift Preferences](assets/discover-details.png)

---

## 🧠 Recommendation Results

![GiftBro Results](assets/results-top.png)

---

## 🏆 Gift Picks

![GiftBro Picks](assets/results-picks.png)

---

## 🔍 Gift Details

![Gift Details](assets/results-details.png)

---

## ✨ Gemini Personalization

![Gemini Personalization](assets/gemini.png)

---

# 📦 Gift Catalogue

GiftBro uses a structured gift catalogue to generate recommendations instead of relying entirely on AI-generated ideas.

The catalogue contains gift information that can be evaluated by the recommendation engine and matched against user preferences.

This allows the system to:

- Recommend actual catalogue candidates
- Compare multiple gift options
- Rank recommendations
- Apply budget constraints
- Match gifts against interests and preferences
- Provide consistent recommendation results

---

# 🗂️ Project Structure

```text
giftbro-ai/
│
├── .github/
│   └── dependabot.yml
│
├── .streamlit/
│
├── assets/
│   ├── home.png
│   ├── discover.png
│   ├── discover-details.png
│   ├── results-top.png
│   ├── results-picks.png
│   ├── results-details.png
│   └── gemini.png
│
├── ai_coach.py
├── api.py
├── app.py
├── database.py
├── gemini_service.py
├── gifts.csv
├── recommender.py
│
├── .gitignore
├── README.md
├── SECURITY.md
└── requirements.txt
```

### Core files

| File | Purpose |
|---|---|
| `app.py` | Streamlit application and user interface |
| `recommender.py` | Recommendation and ranking logic |
| `gemini_service.py` | Gemini-powered personalization |
| `database.py` | SQLite data persistence |
| `api.py` | FastAPI API layer |
| `ai_coach.py` | AI-related application functionality |
| `gifts.csv` | Gift catalogue |
| `requirements.txt` | Python dependencies |
| `.github/dependabot.yml` | Dependency update configuration |

---

# ⚙️ Getting Started

## Prerequisites

Make sure you have:

- Python 3.10+
- pip
- Git

---

## 1. Clone the repository

```bash
git clone https://github.com/singhaasveer-lab/giftbro-ai.git
cd giftbro-ai
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create a local `.env` file for environment-specific configuration.

Add the required Gemini API configuration according to your local setup.

**Never commit API keys or other secrets to GitHub.**

---

## 5. Run GiftBro

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open locally in your browser.

---

# 🔌 API

GiftBro also includes a FastAPI-based API layer.

The API functionality is implemented in:

```text
api.py
```

The API layer allows the recommendation functionality to be exposed beyond the Streamlit interface and provides a foundation for integrating GiftBro with other applications or interfaces.

---

# 💾 Data & Storage

GiftBro uses multiple data sources and storage mechanisms.

### Gift Catalogue

Gift catalogue data is stored in:

```text
gifts.csv
```

### SQLite

SQLite is used for application data such as recommendation history and saved/favorite interactions.

This allows the application to maintain useful user interactions without requiring a separate database server for the project.

---

# 🔐 Security

GiftBro includes repository-level security practices including:

- Dependabot dependency monitoring
- Dependabot security updates
- Dependabot malware alerts
- CodeQL code scanning
- Secret scanning
- Push protection
- Private vulnerability reporting
- Protected `main` branch
- Dependency graph
- Security policy

If you discover a security vulnerability, please report it privately rather than opening a public issue.

See [`SECURITY.md`](SECURITY.md) for the security reporting process.

---

# 🔄 Dependency Management

GiftBro uses Dependabot to help keep Python dependencies up to date.

The repository contains:

```text
.github/dependabot.yml
```

Dependency updates are reviewed through pull requests before being merged into `main`.

The `main` branch is protected to help maintain a clean and reviewable project history.

---

# 🧪 Development

Useful command:

```bash
streamlit run app.py
```

Start the GiftBro application locally.

To install or update project dependencies:

```bash
pip install -r requirements.txt
```

---

# 🚧 Future Improvements

Potential areas for future development include:

- More advanced recommendation ranking
- Improved personalization
- Larger and more diverse gift catalogue
- More recommendation strategies
- Better recommendation explanations
- Enhanced AI-assisted gift coaching
- More API integrations
- Improved deployment support
- More advanced user preference modelling

---

# 👥 Contributors

GiftBro AI is developed collaboratively by:

### Aasveer Singh

AI & Full-Stack Developer

- GitHub: [@singhaasveer-lab](https://github.com/singhaasveer-lab)
- LinkedIn: [Aasveer Singh](https://www.linkedin.com/in/aasveer-singh)

### Akshita Sharda

Collaborator

- GitHub: [@akshita-sharda](https://github.com/akshita-sharda)

---

# 📄 License

This project is currently maintained as a personal development project.

License information will be added when the project is formally licensed.

---

# 🌟 Project Vision

GiftBro is built around a simple idea:

**Good gift recommendations should understand the person, not just the product.**

By combining traditional recommendation techniques with generative AI, GiftBro aims to make gift discovery more relevant, practical, and personal.

```text
Understand the Person
        ↓
Understand the Occasion
        ↓
Find Relevant Gifts
        ↓
Rank the Options
        ↓
Personalize the Recommendation
        ↓
Give a Better Gift 🎁
```

---

## 👨‍💻 Built With

**Python · Streamlit · FastAPI · Scikit-learn · Pandas · SQLite · Google Gemini**

> 🎁 Smarter gifts. Less panic.
