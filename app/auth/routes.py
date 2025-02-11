import re
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth
from app import db
from app.models import User

def is_strong_password(password):
    """
    Check that the password:
    - is at least 8 characters long,
    - contains at least one uppercase letter,
    - contains at least one lowercase letter,
    - contains at least one digit, and
    - contains at least one special character.
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # New fields: first name and last name
        first_name = request.form.get('first_name').strip()
        last_name = request.form.get('last_name').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "danger")
            return redirect(url_for('auth.signup'))
        
        if not is_strong_password(password):
            flash("Password must be at least 8 characters long and include uppercase letters, lowercase letters, digits, and special characters.", "danger")
            return redirect(url_for('auth.signup'))
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email is already registered.", "warning")
            return redirect(url_for('auth.signup'))
        
        # Create a new User record including first and last names.
        new_user = User(first_name=first_name, last_name=last_name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Signup successful! You are now logged in.", "success")
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))
