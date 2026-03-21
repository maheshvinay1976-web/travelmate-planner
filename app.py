from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "travelmate_secret_key"

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ----------------- Models -----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# ----------------- Routes -----------------

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registered Successfully! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Login Successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Credentials!", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Trip Planner
@app.route('/plan', methods=['GET', 'POST'])
def plan():
    if 'user_id' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        destination = request.form['destination']
        days = int(request.form['days'])
        budget = int(request.form['budget'])
        members = int(request.form['members'])

        # Simple calculation: total cost = 1000 per day per member + 5000 fixed
        total_cost = members * days * 1000 + 5000

        return redirect(url_for('result', destination=destination, days=days,
                                budget=budget, members=members, total_cost=total_cost))
    return render_template('planner.html')

# Trip Result
@app.route('/result')
def result():
    if 'user_id' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))

    destination = request.args.get('destination')
    days = int(request.args.get('days', 0))
    budget = int(request.args.get('budget', 0))
    members = int(request.args.get('members', 1))
    total_cost = int(request.args.get('total_cost', 0))

    # Budget status
    if total_cost > budget:
        budget_status = "Budget Exceeded"
        suggestion = "Consider reducing number of days or members."
    else:
        budget_status = "Within Budget"
        suggestion = "You are good to go!"

    # Simple expense breakdown (example)
    expense_breakdown = {
        "Hotel": total_cost * 0.4,
        "Food": total_cost * 0.3,
        "Travel": total_cost * 0.3
    }

    return render_template('result.html',
                           destination=destination,
                           days=days,
                           budget=budget,
                           members=members,
                           total_cost=total_cost,
                           budget_status=budget_status,
                           suggestion=suggestion,
                           expense_breakdown=expense_breakdown)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

# ----------------- Create tables if not exists -----------------
@app.before_first_request
def create_tables():
    db.create_all()

# ----------------- Run App -----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
