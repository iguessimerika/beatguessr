import sqlite3
from pathlib import Path
import utils
import time

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
        cursor.execute("CREATE TABLE IF NOT EXISTS song (songid INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, artist_id INTEGER, mp3_bindata BLOB)")
        
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
    
if __name__ == "__main__":
    users = get_users()
    
    for user in users:
        print(f"Name: {user['username']}")
        
    print(get_user("test@test.de")['password'])