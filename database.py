import sqlite3
import json
from datetime import datetime, timedelta

DB_FILE = 'database.db'

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artists(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                aoty_id INTEGER,
                last_updated TEXT            
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS releases(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist_name TEXT NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                critic_score INTEGER,
                user_score INTEGER,
                must_hear TEXT, defaullt 'no',
                last_updated TEXT,
                UNIQUE(artist_name, name)    
        )
    ''')

    connection.commit()
    connection.close()
    print("Database initialized")


def is_artist_cached(artist_name, max_age_days=7):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT last_updated FROM artists WHERE name = ?",
        (artist_name,)
    )

    row = cursor.fetchone()
    connection.close()

    if not row:
        return False
        
    last_updated = datetime.fromisoformat(row[0])
    return datetime.now() - last_updated < timedelta(days=max_age_days)
    

def save_artist(artist_name, aoty_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO artists (name, aoty_id, last_updated)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            aoty_id = excluded.aoty_id,
            last_updated = excluded.last_updated           
''', (artist_name, aoty_id, datetime.now().isoformat()))
    
    connection.commit()
    connection.close()


def save_releases(releases):
    connection = get_connection()
    cursor = connection.cursor()
    for r in releases:
        cursor.execute('''
            INSERT INTO releases (artist_name, artist_id, name, type, critic_score, user_score, must_hear, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(artist_name, name) DO UPDATE SET
                critic_score = excluded.critic_score,
                user_score = excluded.user_score,
                must_hear = excluded.must_hear,
                last_updated = excluded.last_updated
        ''', (
            r['artist'], r['artist_id'], r['name'], r['type'],
            r.get('critic_score'), r.get('user_score'),
            r.get('must_hear', 'no'), datetime.now().isoformat()
        ))
    connection.commit()
    connection.close()


def get_cached_releases(artist_name):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT artist_name, artist_id, name, type, critic_score, user_score, must_hear FROM releases WHERE artist_name = ?",
        (artist_name,)
    )
    rows = cursor.fetchall()
    connection.close()
    return [
        {
            "artist": row[0],
            "artist_id": row[1],
            "name": row[2],
            "type": row[3],
            "critic_score": row[4],
            "user_score": row[5],
            "must_hear": row[6]
        }
        for row in rows
    ]    