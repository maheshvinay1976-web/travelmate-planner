from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("database.db")

def create_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_table()

# ---------- HOME ----------
@app.route('/')
def home():
    return redirect('/login')

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return "Invalid login"

    return render_template('login.html')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

# ---------- PLAN ----------
@app.route('/plan', methods=['GET', 'POST'])
def plan():
    if request.method == 'POST':
        budget = int(request.form['budget'])
        days = int(request.form['days'])
        people = int(request.form['people'])

        # AI Logic
   # AI Logic
def recommend_plan(budget, days):
    if budget < 5000:
        destination = "Nearby Places"
        hotel_type = "Budget Stay"
    elif budget < 20000:
        destination = "Goa / Mysore / Ooty"
        hotel_type = "3 Star Hotel"
    else:
        destination = "Manali / Kashmir"
        hotel_type = "5 Star Hotel"

    return destination, hotel_type
    
        # Cost Calculation
        def calculate_cost(days, people):
    hotel = days * 1200
    food = days * 600 * people
    travel = 2500

    total = hotel + food + travel

    return hotel, food, travel, total

        return render_template('result.html',
                               destination=destination,
                               total=total)

    return render_template('plan.html')

def generate_itinerary(days):
    itinerary = []

    for i in range(1, days + 1):
        if i == 1:
            plan = "Arrival & Local Sightseeing"
        elif i == days:
            plan = "Shopping & Departure"
        else:
            plan = "Explore Tourist Places & Activities"

        itinerary.append(f"Day {i}: {plan}")

    return itinerary
@app.route('/plan', methods=['GET', 'POST'])
def plan():
    if request.method == 'POST':
        budget = int(request.form['budget'])
        days = int(request.form['days'])
        people = int(request.form['people'])

        destination, hotel_type = recommend_plan(budget, days)

        hotel, food, travel, total = calculate_cost(days, people)

        itinerary = generate_itinerary(days)

        # Smart suggestion
        suggestion = ""
        if budget < 5000:
            suggestion = "Budget is low, try reducing number of days."
        elif budget > 30000:
            suggestion = "You can upgrade to premium experiences!"

        return render_template('result.html',
                               destination=destination,
                               hotel_type=hotel_type,
                               hotel=hotel,
                               food=food,
                               travel=travel,
                               total=total,
                               itinerary=itinerary,
                               suggestion=suggestion)

    return render_template('plan.html')

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
