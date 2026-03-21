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

# --------------------
# Database Models
# --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# --------------------
# Routes
# --------------------

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        # Check if email already exists
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
        try:
            days = int(request.form['days'])
        except ValueError:
            flash("Invalid number of days!", "danger")
            return redirect(url_for('plan'))

        try:
            members = int(request.form['members'])
        except ValueError:
            flash("Invalid number of members!", "danger")
            return redirect(url_for('plan'))

        try:
            budget = int(request.form['budget'])
        except ValueError:
            flash("Invalid budget!", "danger")
            return redirect(url_for('plan'))

        # Simple total cost calculation (customize as needed)
        cost_per_person_per_day = 5000
        total_cost = days * members * cost_per_person_per_day
        status = "Within Budget" if total_cost <= budget else "Budget Exceeded"
        suggestion = "Adjust your trip or increase budget." if total_cost > budget else "Enjoy your trip!"

        flash(f"Trip to {destination} planned successfully!", "success")
        return redirect(url_for('result',
                                destination=destination,
                                days=days,
                                members=members,
                                total_cost=total_cost,
                                budget=budget,
                                status=status,
                                suggestion=suggestion))

    return render_template('planner.html')

# Trip Result
@app.route('/result')
def result():
    if 'user_id' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))

    destination = request.args.get('destination')
    days = request.args.get('days')
    members = request.args.get('members')
    total_cost = request.args.get('total_cost')
    budget = request.args.get('budget')
    status = request.args.get('status')
    suggestion = request.args.get('suggestion')

    # Example expense breakdown
    hotel = int(days) * int(members) * 2000
    food = int(days) * int(members) * 1500
    travel = int(days) * int(members) * 1500

    return render_template('result.html',
                           destination=destination,
                           days=days,
                           members=members,
                           total_cost=total_cost,
                           budget=budget,
                           status=status,
                           suggestion=suggestion,
                           hotel=hotel,
                           food=food,
                           travel=travel)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

# --------------------
# Main
# --------------------
if __name__ == '__main__':
    # Create DB if not exists
    if not os.path.exists("database.db"):
        db.create_all()

    port = int(os.environ.get("PORT", 5000))  # Render assigns a port
    app.run(host='0.0.0.0', port=port, debug=True)
