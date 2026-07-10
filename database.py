import sqlite3
from datetime import datetime, timedelta

DB_FILE = 'database.db'


def get_connection():
    """Open and return a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)


def init_db():
    """Create the database tables if they don't already exist.

    Called once at startup in main.py. Safe to call repeatedly — uses
    CREATE TABLE IF NOT EXISTS so it won't overwrite existing data.
    """
    connection = get_connection()
    cursor = connection.cursor()

    # Stores the numeric genre ID that AOTY embeds in its URLs (e.g. '38' for hip-hop).
    # We extract this from the user chart page and reuse it to build critic chart URLs.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS genre_ids(
            slug TEXT PRIMARY KEY,
            genre_id TEXT NOT NULL
        )
    ''')

    # Caches chart results per genre so we don't re-scrape AOTY on every run.
    # Each row is one album entry for a genre. Expires after 7 days (checked in is_genre_chart_cached).
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS genre_chart_cache(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            genre_slug TEXT NOT NULL,
            artist TEXT NOT NULL,
            name TEXT NOT NULL,
            critic_score INTEGER,
            user_score INTEGER,
            user_ratings INTEGER DEFAULT 0,
            critic_reviews INTEGER DEFAULT 0,
            last_updated TEXT,
            UNIQUE(genre_slug, artist, name)
        )
    ''')

    connection.commit()
    connection.close()
    print("Database initialized")


def save_genre_id(slug, genre_id):
    """Save the numeric AOTY genre ID for a genre slug (e.g. 'hip-hop' -> '38').

    Uses ON CONFLICT DO NOTHING so re-scraping won't overwrite an existing value.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO genre_ids (slug, genre_id)
        VALUES (?, ?)
        ON CONFLICT(slug) DO NOTHING
    ''', (slug, genre_id))
    conn.commit()
    conn.close()


def get_genre_id(slug):
    """Return the stored numeric AOTY genre ID for a slug, or None if not yet known."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT genre_id FROM genre_ids WHERE slug = ?", (slug,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def is_genre_chart_cached(genre_slug, max_age_days=7):
    """Return True if fresh chart data for this genre exists in the cache."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT last_updated FROM genre_chart_cache WHERE genre_slug = ? LIMIT 1",
        (genre_slug,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False
    last_updated = datetime.fromisoformat(row[0])
    return datetime.now() - last_updated < timedelta(days=max_age_days)


def save_genre_chart_results(genre_slug, results, score_field):
    """Upsert a list of album chart results into the cache for a genre.

    score_field: 'user_score' or 'critic_score' — determines which columns are written.
    Called twice per genre fetch (once for each score type) so both columns get populated.
    """
    conn = get_connection()
    cursor = conn.cursor()
    for r in results:
        score_value = r.get(score_field)
        if score_field == 'user_score':
            cursor.execute('''
                INSERT INTO genre_chart_cache (genre_slug, artist, name, user_score, user_ratings, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(genre_slug, artist, name) DO UPDATE SET
                    user_score = excluded.user_score,
                    user_ratings = excluded.user_ratings,
                    last_updated = excluded.last_updated
            ''', (genre_slug, r['artist'], r['name'], score_value, r.get('user_ratings', 0), datetime.now().isoformat()))
        else:
            cursor.execute('''
                INSERT INTO genre_chart_cache (genre_slug, artist, name, critic_score, critic_reviews, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(genre_slug, artist, name) DO UPDATE SET
                    critic_score = excluded.critic_score,
                    critic_reviews = excluded.critic_reviews,
                    last_updated = excluded.last_updated
            ''', (genre_slug, r['artist'], r['name'], score_value, r.get('critic_reviews', 0), datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_cached_genre_chart(genre_slug):
    """Return all cached album entries for a genre as a list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT artist, name, critic_score, user_score, user_ratings, critic_reviews
           FROM genre_chart_cache WHERE genre_slug = ?""",
        (genre_slug,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "artist": row[0],
            "name": row[1],
            "critic_score": row[2],
            "user_score": row[3],
            "user_ratings": row[4] or 0,
            "critic_reviews": row[5] or 0
        }
        for row in rows
    ]
