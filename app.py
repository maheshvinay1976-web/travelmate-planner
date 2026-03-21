from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "travelmate_secret_key"

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Home Page
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

# Planner Page
@app.route('/plan', methods=['GET', 'POST'])
def plan():
    if 'user_id' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        destination = request.form['destination']
        days = int(request.form['days'])
        budget = int(request.form['budget'])

        # Example: simple calculation of total cost
        cost_per_day = 5000  # hotel + food + travel
        total_cost = cost_per_day * days

        # Check budget
        if total_cost > budget:
            status = "Budget Exceeded"
            suggestion = f"Consider reducing stay by {((total_cost-budget)//cost_per_day)} days or cheaper options."
        else:
            status = "Within Budget"
            suggestion = "Your budget is sufficient!"

        # Expense breakdown
        breakdown = {
            "Hotel": 0.5 * total_cost,
            "Food": 0.3 * total_cost,
            "Travel": 0.2 * total_cost
        }

        # Pass all info to result page
        return redirect(url_for(
            'result',
            destination=destination,
            days=days,
            total_cost=total_cost,
            budget=budget,
            status=status,
            suggestion=suggestion,
            hotel=breakdown["Hotel"],
            food=breakdown["Food"],
            travel=breakdown["Travel"]
        ))
    return render_template('planner.html')

# Result Page
@app.route('/result')
def result():
    if 'user_id' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))

    # Get all trip info from query parameters
    destination = request.args.get('destination')
    days = request.args.get('days')
    total_cost = request.args.get('total_cost')
    budget = request.args.get('budget')
    status = request.args.get('status')
    suggestion = request.args.get('suggestion')
    hotel = request.args.get('hotel')
    food = request.args.get('food')
    travel = request.args.get('travel')

    flash("Trip calculated successfully!", "success")
    return render_template('result.html',
                           destination=destination,
                           days=days,
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
import os

if __name__ == '__main__':
    # Ensure tables exist
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get("PORT", 5000))  # Use Render's dynamic port
    app.run(host='0.0.0.0', port=port, debug=True)
