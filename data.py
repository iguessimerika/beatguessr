import sqlite3
from pathlib import Path
import utils
import time
from flask import jsonify

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'beatguessr.db'

def get_connection() -> sqlite3.Connection:
    
    connection = sqlite3.connect(DB_PATH)
    connection .row_factory = sqlite3.Row
    return connection


    
def init_database():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # create table SONG
        cursor.execute("CREATE TABLE IF NOT EXISTS song (songid INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, artist_id INTEGER, mp3_filepath TEXT)")
        
        # create table ARTIST
        cursor.execute("CREATE TABLE IF NOT EXISTS artist (artistid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        
        # create table USER
        cursor.execute("CREATE TABLE IF NOT EXISTS user (userid INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, register_date INTEGER, email TEXT)")
        
        # create table HINT
        cursor.execute("CREATE TABLE IF NOT EXISTS hint (hintid INTEGER PRIMARY KEY AUTOINCREMENT, song_id INTEGER, hint_number INTEGER, hint_text TEXT)")
        
        # create table GUESS
        cursor.execute("CREATE TABLE IF NOT EXISTS guess (guessid INTEGER PRIMARY KEY AUTOINCREMENT, song_id INTEGER, user_id INTEGER, seconds INTEGER)")
        
        conn.commit()
        
        
def add_user(username, password, email):
    with get_connection() as conn:
        cursor = conn.cursor()
        date_ms = int(time.time()*1000.0)
        hashed_pw = utils.hash_password(password)
        cursor.execute(
            "INSERT INTO user (username, password, register_date, email) VALUES (?, ?, ?, ?)",
            (username, hashed_pw, date_ms, email)
        )
        
        conn.commit()
        

def get_users():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        return cursor.fetchall()
        
def get_user(email):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM user WHERE email = '{email}'")
        
        user = cursor.fetchone()
        return user or "no-user"
    
def get_user_id(username):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT userid FROM user WHERE username = '{username}'")
        
        userid = cursor.fetchone()['userid']
        
        return int(userid)
    

def add_artist(name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO artist (name) VALUES (?)",
            (name,)
        )
        
        conn.commit()
        
        return get_artistid(name)
    
    
def get_artistid(name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT artistid FROM artist WHERE name = '{name}'")
        
        artistid = cursor.fetchone()['artistid']
        
        return int(artistid)


def get_artists():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM artist")
        return cursor.fetchall()
    
def search_artists(query):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        if not query:
            return jsonify([])
        
        artists = cursor.execute(
        "SELECT artistid, name FROM artist WHERE name LIKE ?"
        , (f"%{query}%",)).fetchall()
        
        return jsonify([dict(artist) for artist in artists])
        

def add_song(title, artist_id, filepath):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO song (title, artist_id, mp3_filepath) VALUES (?, ?, ?)",
            (title, artist_id, filepath)
        )
        
        conn.commit()
        
        return get_songid(title, artist_id)
        

def get_songid(title, artist_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT songid FROM song WHERE title = '{title}' AND artist_id = '{artist_id}'")
        
        songid = cursor.fetchone()['songid']
        
        return int(songid)
    

def get_songs():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM song")
        
        return cursor.fetchall()
    

def search_songs(query, artist):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        if not query or not artist:
            return jsonify([])
        
        songs = cursor.execute("""
        SELECT song.songid, song.title 
        FROM song
        JOIN artist ON song.artist_id = artist.artistid
        WHERE song.title LIKE ? AND artist.name = ?""", (f"%{query}%", artist)).fetchall()
        
        return jsonify([dict(song) for song in songs])
        
        
def add_hint(message, song_id, hint_number):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO hint (hint_text, song_id, hint_number) VALUES (?, ?, ?)",
            (message, song_id, hint_number)
        )
        
        conn.commit()

def get_song_hints(songid):
    with get_connection() as conn:
        cursor = conn.cursor()
        hints = cursor.execute(
            f"SELECT hint_number, hint_text FROM hint WHERE song_id = '{songid}'"
            ).fetchall()
        
        return hints


def add_guess(song_id, user_id, seconds):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO guess (song_id, user_id, seconds) VALUES (?, ?, ?)",
            (song_id, user_id, seconds)
        )
        
        conn.commit()
        

def get_song_guesses(song_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id, seconds FROM guess WHERE song_id = '{song_id}' ORDER BY seconds ASC")
        
        return cursor.fetchall()




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