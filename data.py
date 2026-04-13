import os
import time
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import jsonify

import utils

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL ist nicht gesetzt.")

    return psycopg2.connect(DATABASE_URL, sslmode="require")


def init_database():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # create table ARTIST
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS artist (
                    artistid SERIAL PRIMARY KEY,
                    name TEXT
                )
            """)

            # create table SONG
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS song (
                    songid SERIAL PRIMARY KEY,
                    title TEXT,
                    artist_id INTEGER REFERENCES artist(artistid),
                    mp3_filepath TEXT
                )
            """)

            # create table USER
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    userid SERIAL PRIMARY KEY,
                    username TEXT,
                    password TEXT,
                    register_date BIGINT,
                    email TEXT
                )
            """)

            # create table HINT
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hint (
                    hintid SERIAL PRIMARY KEY,
                    song_id INTEGER REFERENCES song(songid),
                    hint_number INTEGER,
                    hint_text TEXT
                )
            """)

            # create table GUESS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS guess (
                    guessid SERIAL PRIMARY KEY,
                    song_id INTEGER REFERENCES song(songid),
                    user_id INTEGER REFERENCES users(userid),
                    seconds INTEGER
                )
            """)

        conn.commit()


def add_user(username, password, email):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            date_ms = int(time.time() * 1000.0)
            hashed_pw = utils.hash_password(password)

            cursor.execute("""
                INSERT INTO users (username, password, register_date, email)
                VALUES (%s, %s, %s, %s)
            """, (username, hashed_pw, date_ms, email))

        conn.commit()


def get_users():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM users')
            return cursor.fetchall()


def get_user(email):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            return user or "no-user"


def get_user_by_id(userid):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM users WHERE userid = %s', (userid,))
            user = cursor.fetchone()
            return user or "no-user"
        

def user_exists(userid, username, email):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM users WHERE username = %s AND email = %s AND userid != %s', (username, email, userid))
            user = cursor.fetchone()
            return user or "no-user"


def get_user_id(username):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT userid FROM users WHERE username = %s', (username,))
            row = cursor.fetchone()
            return int(row["userid"]) if row else None
        
def change_user_data(userid, columns, values):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            counter = 0;
            query = "UPDATE users SET "
            updates = []
            
            for column in columns:
                updates.append(f"{column} = '{values[counter]}'")
                
            query += ", ".join(updates)
            
            cursor.execute(query + f" WHERE userid = '{userid}'")
        
            conn.commit()


def add_artist(name):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO artist (name) VALUES (%s) RETURNING artistid",
                (name,)
            )
            artistid = cursor.fetchone()[0]

        conn.commit()
        return int(artistid)


def get_artistid(name):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT artistid FROM artist WHERE name = %s", (name,))
            row = cursor.fetchone()
            return int(row["artistid"]) if row else None


def get_artist_name(artistid):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT name FROM artist WHERE artistid = %s", (artistid,))
            row = cursor.fetchone()
            return row["name"] if row else None


def get_artists():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM artist")
            return cursor.fetchall()


def search_artists(query):
    if not query:
        return jsonify([])

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT DISTINCT artistid, name FROM artist WHERE name ILIKE %s",
                (f"%{query}%",)
            )
            artists = cursor.fetchall()
            return jsonify(artists)


def add_song(title, artist_id, filepath):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO song (title, artist_id, mp3_filepath)
                VALUES (%s, %s, %s)
                RETURNING songid
            """, (title, artist_id, filepath))
            songid = cursor.fetchone()[0]

        conn.commit()
        return int(songid)


def get_songid(title, artist_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT songid FROM song WHERE title = %s AND artist_id = %s",
                (title, artist_id)
            )
            row = cursor.fetchone()
            return int(row["songid"]) if row else None


def get_song_title(songid):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT title FROM song WHERE songid = %s", (songid,))
            row = cursor.fetchone()
            return row["title"] if row else None


def get_songs():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM song")
            return cursor.fetchall()


def search_songs(query, artist):
    if not query or not artist:
        return jsonify([])

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT DISTINCT song.songid, song.title
                FROM song
                JOIN artist ON song.artist_id = artist.artistid
                WHERE song.title ILIKE %s AND artist.name = %s
            """, (f"%{query}%", artist))
            songs = cursor.fetchall()
            return jsonify(songs)


def add_hint(message, song_id, hint_number):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO hint (hint_text, song_id, hint_number)
                VALUES (%s, %s, %s)
            """, (message, song_id, hint_number))

        conn.commit()


def get_song_hints(songid):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT hint_number, hint_text
                FROM hint
                WHERE song_id = %s
                ORDER BY hint_number ASC
            """, (songid,))
            return cursor.fetchall()


def add_guess(song_id, user_id, seconds):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO guess (song_id, user_id, seconds)
                VALUES (%s, %s, %s)
            """, (song_id, user_id, seconds))

        conn.commit()


def get_song_guesses(song_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT users.username, MIN(guess.seconds) AS best_time
                FROM guess
                JOIN users ON guess.user_id = users.userid
                WHERE guess.song_id = %s
                GROUP BY users.userid, users.username
                ORDER BY best_time ASC
            """, (song_id,))
            return cursor.fetchall()


def get_user_songs(user_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT DISTINCT guess.song_id, song.title, artist.name
                FROM guess
                JOIN song ON guess.song_id = song.songid
                JOIN artist ON song.artist_id = artist.artistid
                WHERE guess.user_id = %s
            """, (user_id,))
            songs = cursor.fetchall()
            return [dict(song) for song in songs]

if __name__ == "__main__":
    
    init_database()
    
    users = get_users()
    
    for user in users:
        print(f"Name: {user['username']}")
        
    artists = get_artists()
    
    for artist in artists:
        print(f"ArtistId: {artist['artistid']}")
        
    songs = get_songs()
    
    for song in songs:
        print(f"SongId: {song['songid']} - Name: {song['title']} - Artist ID: {song['artist_id']}")

        guesses = get_song_guesses(song['songid'])
        for guess in guesses:
            print(f"  User ID: {guess['user_id']} - Seconds: {guess['seconds']}")