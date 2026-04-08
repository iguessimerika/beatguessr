from flask import Flask, request, render_template, session, redirect, url_for, send_from_directory, jsonify
import data, utils, os, game

app = Flask(__name__)
app.secret_key = "supersecretkey"  # wichtig für Sessions!
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    data.init_database()
    
    if not session.get('logged_in'):
        return render_template("index.html")
    return render_template("dashboard.html")


@app.route("/registrierung")
def registrierung():
    return render_template("registrierung.html")

@app.route('/registrierung', methods=['POST'])
def add_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    data.add_user(username, password, email)
    
    session['logged_in'] = True
    session['current_email'] = email
    session['current_username'] = username
    return redirect(url_for('dashboard'))
    

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def pw_check():
    error_msg = None
    email = request.form['email']
    password = request.form['password']
    
    user = data.get_user(email)
    
    if user == "no-user":
        error_msg = "Kein Benutzer mit dieser E-Mail Adresse hinterlegt!"
    else:
        username = user['username']
        user_pw = user['password']

        if utils.check_password(password, user_pw):
            session['logged_in'] = True
            session['current_email'] = email
            session['current_username'] = username
            return redirect(url_for('dashboard'))
        else:
            error_msg = "Falsches Passwort!"
    
    return render_template("login.html", error=error_msg)
    
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template("dashboard.html", name=session['current_username'])

@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")

# Mein Profil
@app.route("/profil")
def profil():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    
    username = session['current_username']
    user_id = data.get_user_id(username)
    
    context = {
        "username": username
    }
    
    return render_template("mein-profil.html", **context)


# Spiel starten
@app.route("/play")
def play():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    
    artists = data.get_artists()
    songs = data.get_songs()
    
    song_structure = game.build_song_structure(artists, songs)
    
    random_song = game.random_song()
    song_artistid = random_song['artist_id']
    song_id = random_song['songid']
    hints = game.get_hints(song_id)
    
    url = random_song['mp3_filepath']
    
    context = {
        "artist": song_artistid,
        "song": song_id,
        "data": song_structure,
        "hint1": hints[1],
        "hint2": hints[2],
        "song_url": url,
        "username": session['current_username']
    }
    
    return render_template("spiel_start.html", **context)

# Artist Dropdown Suche beim Raten
@app.route("/search_artists")
def search_artists():
    query = request.args.get("q", "")

    artists = data.search_artists(query)
    
    return artists

# Song Dropdown Suche beim Raten
@app.route("/search_songs")
def search_songs():
    query = request.args.get("q", "")
    artist = request.args.get("artist", "")

    return data.search_songs(query, artist)


# Gewonnen Screen
@app.route("/win")
def win():
    time = request.args.get("time", None)
    username = request.args.get("username", None)
    artist_id = request.args.get("artist_id", None)
    song_id = request.args.get("song_id", None)

    user_id = data.get_user_id(username)

    data.add_guess(song_id, user_id, time)
    
    artist = data.get_artist_name(artist_id)
    title = data.get_song_title(song_id)

    context = {
        "username": username,
        "time": time,
        "artist": artist,
        "title": title
    }

    return render_template("win-screen.html", **context)

#verloren Screen

# Gewonnen Screen
@app.route("/loose")
def loose():
    time = request.args.get("time", None)
    username = request.args.get("username", None)
    artist_id = request.args.get("artist_id", None)
    song_id = request.args.get("song_id", None)

    user_id = data.get_user_id(username)

    data.add_guess(song_id, user_id, time)
    
    artist = data.get_artist_name(artist_id)
    title = data.get_song_title(song_id)

    context = {
        "username": username,
        "time": time,
        "artist": artist,
        "title": title
    }

    return render_template("loose-screen.html", **context)



@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory('uploads', filename)

@app.route('/upload')
def upload_site():
    artists = data.get_artists()
    return render_template("upload.html", artists=artists)

@app.route('/upload', methods=['POST'])
def upload():
    title = request.form['title']
    artist_id = request.form.get('artist_id')
    new_artist = request.form.get('new_artist')
    file = request.files['mp3']

    # Artist Logik
    if new_artist:
        # neuen Artist erstellen
        artist_id = data.add_artist(new_artist)
    else:
        artist_id = int(artist_id)

    # Datei speichern
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Song speichern
        song_id = data.add_song(title, artist_id, filepath)

        message = "Song erfolgreich hochgeladen!"
    else:
        message = "Fehler beim Upload!"
        
    # Hinweise speichern
    hints = [["1", request.form.get('hint1')], ["2", request.form.get('hint2')]]
    
    for hint in hints:
        data.add_hint(hint[1], song_id, hint[0])
    

    artists = data.get_artists()
    return render_template("upload.html", artists=artists, message=message)

if __name__ == "__main__":
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # max. 10 MB
    app.run(debug=True)