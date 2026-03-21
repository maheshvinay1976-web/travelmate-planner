from flask import Flask, render_template, request, redirect, session, flash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "secret123"   # change later for security
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ✅ DATABASE CONNECTION
def get_db_connection():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))


# ✅ CREATE TABLES (RUN ON START)
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS trips (
        id SERIAL PRIMARY KEY,
        username TEXT,
        destination TEXT,
        days INTEGER,
        total_cost INTEGER
    )
    """)

    conn.commit()
    cur.close()
    conn.close()


init_db()


# ✅ HOME → LOGIN PAGE
@app.route('/')
def home():
    return redirect('/login')


# ✅ REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, password))

        conn.commit()
        cur.close()
        conn.close()

        flash("Registration successful! Please login.", "success")
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                    (username, password))
        user = cur.fetchone()

        if user:
            session['user'] = username   # ✅ MUST
            print("SESSION SET:", session)  # DEBUG
            flash("Login successful!", "success")
            return redirect('/dashboard')   # ✅ MUST

        else:
            flash("Invalid username or password", "error")

    return render_template('index.html')

# ✅ LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully", "success")
    return redirect('/login')


# ✅ PLAN TRIP PAGE
@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        flash("Please login first!", "error")
        return redirect('/login')

    if request.method == 'POST':
        destination = request.form['destination']
        days = int(request.form['days'])
        budget = int(request.form['budget'])

        # Simple calculation
        hotel = budget * 0.4
        food = budget * 0.3
        travel = budget * 0.3

        suggestion = f"Enjoy your trip to {destination}! Plan wisely."

        # SAVE TO DATABASE
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO trips (username, destination, days, total_cost)
            VALUES (%s, %s, %s, %s)
        """, (session['user'], destination, days, budget))

        conn.commit()
        conn.close()

        return render_template('result.html',
                               destination=destination,
                               total=budget,
                               hotel=hotel,
                               food=food,
                               travel=travel,
                               suggestion=suggestion)

    return render_template('index.html')


# ✅ DASHBOARD
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


# ✅ DELETE TRIP
@app.route('/delete_trip/<int:id>', methods=['POST'])
def delete_trip(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM trips WHERE id = %s", (id,))
    
    conn.commit()
    cur.close()
    conn.close()

    flash("Trip deleted successfully!", "success")
    return redirect('/dashboard')


# ✅ RUN APP (FOR LOCAL ONLY)
import os

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
