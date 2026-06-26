from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import abort, current_app
import os
from werkzeug.utils import secure_filename

auth_bp = Blueprint('auth', __name__)

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin': return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'startup': return redirect(url_for('startup.dashboard'))
        else: return redirect(url_for('investor.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'startup':
                return redirect(url_for('startup.dashboard'))
            else:
                return redirect(url_for('investor.dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        role = request.form.get('role')
        
        if role not in ['investor', 'startup']:
            flash('Invalid role selected.', 'danger')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))

        employer_company = request.form.get('employer_company')
        
        file = request.files.get('national_id')
        national_id_path = None
        if file and '.' in file.filename:
            filename = secure_filename(file.filename)
            unique_name = f"nid_{email}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name))
            national_id_path = unique_name
            
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password_hash=hashed_password, phone=phone, role=role, national_id_path=national_id_path, employer_company=employer_company)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
