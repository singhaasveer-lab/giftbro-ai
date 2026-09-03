import sqlite3
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "giftbro.db"


def get_connection():
    connection = sqlite3.connect(
        DB_FILE
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create all application tables."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS recommendation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            recipient TEXT NOT NULL,
            age INTEGER,
            relationship TEXT,
            occasion TEXT,
            interests TEXT,
            personality TEXT,
            budget INTEGER,
            selected_gifts TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS favorite_gifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            gift_name TEXT NOT NULL UNIQUE,
            category TEXT,
            price INTEGER,
            match_score REAL,
            description TEXT,
            personalization TEXT
        )
        """
    )

    connection.commit()
    connection.close()


def save_recommendation(
    recipient,
    age,
    relationship,
    occasion,
    interests,
    personality,
    budget,
    selected_gifts,
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO recommendation_history (
            created_at,
            recipient,
            age,
            relationship,
            occasion,
            interests,
            personality,
            budget,
            selected_gifts
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(
                timespec="seconds"
            ),
            recipient,
            int(age),
            relationship,
            occasion,
            interests,
            personality,
            int(budget),
            selected_gifts,
        ),
    )

    connection.commit()
    connection.close()


def get_history(limit=20):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM recommendation_history
        ORDER BY id DESC
        LIMIT ?
        """,
        (int(limit),),
    )

    rows = cursor.fetchall()

    connection.close()

    return rows


def save_favorite(
    gift_name,
    category,
    price,
    match_score,
    description,
    personalization,
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM favorite_gifts
        WHERE gift_name = ?
        """,
        (gift_name,),
    )

    existing = cursor.fetchone()

    if existing:
        connection.close()
        return False

    cursor.execute(
        """
        INSERT INTO favorite_gifts (
            created_at,
            gift_name,
            category,
            price,
            match_score,
            description,
            personalization
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(
                timespec="seconds"
            ),
            gift_name,
            category,
            int(price),
            float(match_score),
            description,
            personalization,
        ),
    )

    connection.commit()
    connection.close()

    return True


def get_favorites():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM favorite_gifts
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return rows


def favorite_exists(gift_name):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM favorite_gifts
        WHERE gift_name = ?
        """,
        (gift_name,),
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None


def delete_favorite(favorite_id):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM favorite_gifts
        WHERE id = ?
        """,
        (int(favorite_id),),
    )

    connection.commit()
    connection.close()


# Initialize automatically when imported.
initialize_database()