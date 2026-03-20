from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"   # Required for flash & session

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS trips(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        destination TEXT,
        days INTEGER,
        people INTEGER,
        budget INTEGER,
        total_cost INTEGER)''')

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        # Check if user already exists
        cur.execute("SELECT * FROM users WHERE username=?", (user,))
        existing = cur.fetchone()

        if existing:
            flash("Username already exists!", "error")
        else:
            cur.execute("INSERT INTO users(username,password) VALUES(?,?)",(user,pwd))
            conn.commit()
            flash("Registration successful! Please login.", "success")

        conn.close()
        return redirect('/login')

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        data = cur.fetchone()
        conn.close()

        if data:
            session['user'] = user
            flash("Login successful!", "success")
            return redirect('/dashboard')
        else:
            flash("Invalid username or password", "error")

    return render_template('login.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("Please login first!", "error")
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM trips WHERE username=?", (session['user'],))
    trips = cur.fetchall()
    conn.close()

    return render_template('dashboard.html', trips=trips)

# ---------------- PLANNER ----------------
@app.route('/planner')
def planner():
    if 'user' not in session:
        flash("Please login to plan a trip!", "error")
        return redirect('/login')

    return render_template('planner.html')

# ---------------- RESULT ----------------
@app.route('/result', methods=['POST'])
def result():
    if 'user' not in session:
        flash("Please login first!", "error")
        return redirect('/login')

    destination = request.form['destination']
    days = int(request.form['days'])
    people = int(request.form['people'])
    budget = int(request.form['budget'])

    # Cost calculation
    hotel = days * 1500
    food = days * 500 * people
    travel = 2000 * people

    total = hotel + food + travel

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("""INSERT INTO trips(username,destination,days,people,budget,total_cost)
                   VALUES(?,?,?,?,?,?)""",
                (session['user'], destination, days, people, budget, total))
    conn.commit()
    conn.close()

    flash("Trip calculated successfully!", "success")

    return render_template('result.html',
                           destination=destination,
                           total=total,
                           budget=budget)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "success")
    return redirect('/')

# ---------------- RUN ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
