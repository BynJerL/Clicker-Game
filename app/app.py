from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple-secret-key'  # For flash messages and sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    year_of_birth = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    clicks = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Create database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['user_name']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('user_page'))
        flash('Invalid username or password')
    return render_template('login_page.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        year_of_birth = request.form['year_of_birth']
        username = request.form['user_name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Password do not match')
            return render_template("register.html")
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        try:
            year_of_birth = int(year_of_birth)
            current_year = date.today().year
            if year_of_birth < 1900 or year_of_birth > current_year:
                flash("Invalid year of birth")
                return render_template('register.html')
        except ValueError:
            flash('Year of birth must be a number')
            return render_template('register.html')

        user = User(username=username,
                    fullname=full_name,
                    email=email,
                    year_of_birth=year_of_birth)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/user_page', methods=['GET', 'POST'])
def user_page():
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.clicks += 1
        db.session.commit()
    return render_template('user_page.html', username=user.username, click_count=user.clicks)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(debug=True)