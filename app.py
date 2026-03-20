from flask import Flask, render_template, request, redirect, session, flash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))

# ---------------- INIT DATABASE ----------------
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS trips(
        id SERIAL PRIMARY KEY,
        username TEXT,
        destination TEXT,
        days INTEGER,
        people INTEGER,
        budget INTEGER,
        total_cost INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=%s", (user,))
        existing = cur.fetchone()

        if existing:
            flash("Username already exists!", "error")
        else:
            cur.execute("INSERT INTO users(username,password) VALUES(%s,%s)", (user, pwd))
            conn.commit()
            flash("Registration successful! Please login.", "success")

        conn.close()
        return redirect('/login')

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (user, pwd))
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

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM trips WHERE username=%s", (session['user'],))
    trips = cur.fetchall()

    # Analytics
    cur.execute("SELECT SUM(total_cost) FROM trips WHERE username=%s", (session['user'],))
    total_spent = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM trips WHERE username=%s", (session['user'],))
    total_trips = cur.fetchone()[0]

    conn.close()

    return render_template('dashboard.html',
                           trips=trips,
                           total_spent=total_spent,
                           total_trips=total_trips)

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

    # 🔥 FIXED Suggestion Logic
    if total > budget:
        suggestion = "⚠ Your budget is low. Consider reducing days or expenses."
    elif total < budget * 0.5:
        suggestion = "💡 You can upgrade your trip with better hotels!"
    else:
        suggestion = "✅ Your budget is perfect!"

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO trips(username,destination,days,people,budget,total_cost)
        VALUES(%s,%s,%s,%s,%s,%s)
    """, (session['user'], destination, days, people, budget, total))

    conn.commit()
    conn.close()

    flash("Trip calculated successfully!", "success")

    # ✅ IMPORTANT: Passing suggestion to HTML
    return render_template('result.html',
                           destination=destination,
                           total=total,
                           budget=budget,
                           hotel=hotel,
                           food=food,
                           travel=travel,
                           suggestion=suggestion)

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
