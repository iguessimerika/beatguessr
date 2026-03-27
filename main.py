from flask import Flask, request, render_template, session, redirect, url_for
import data, utils, os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # wichtig für Sessions!
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    data.init_database()

    session.clear()
    
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
    print(user)
    
    if user == "no-user":
        error_msg = "Kein Benutzer mit dieser E-Mail Adresse hinterlegt!"
    else:
        user_pw = user['password']

        if utils.check_password(password, user_pw):
            session['logged_in'] = True
            session['current_email'] = email
            return redirect(url_for('dashboard'))
        else:
            error_msg = "Falsches Passwort!"
    
    return render_template("login.html", error=error_msg)
    
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")

@app.route("/spiel-starten")
def spiel_starten():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template("spiel_start.html")

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

    # ---- Artist Logik ----
    if new_artist:
        # neuen Artist erstellen
        artist_id = data.add_artist(new_artist)
    else:
        artist_id = int(artist_id)

    # ---- Datei speichern ----
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # ---- Song speichern ----
        song_id = data.add_song(title, artist_id, filepath)

        message = "Song erfolgreich hochgeladen!"
    else:
        message = "Fehler beim Upload!"
        
    # ---- Hinweise speichern ----
    hints = [["1", request.form.get('hint1')], ["2", request.form.get('hint2')]]
    
    for hint in hints:
        print(song_id)
        data.add_hint(hint[1], song_id, hint[0])
    

    artists = data.get_artists()
    return render_template("upload.html", artists=artists, message=message)

if __name__ == "__main__":
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # max. 10 MB
    app.run(debug=True)