from flask import Flask, request, render_template, session, redirect, url_for
import data, utils

app = Flask(__name__)
app.secret_key = "supersecretkey"  # wichtig für Sessions!

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
    
    print("Test")
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

if __name__ == "__main__":
    app.run(debug=True)