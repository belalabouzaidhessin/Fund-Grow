import os

base_dir = "D:/fundgrow"

files = {
    "requirements.txt": """Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
Werkzeug==3.0.1
PyMySQL==1.1.0
cryptography
email_validator
python-dotenv
""",
    "config.py": """import os

class Config:
    SECRET_KEY = 'super-secret-fundgrow-key-2026'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/fundgrow'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
""",
    "app.py": """import os
from flask import Flask
from config import Config
from models import db
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.investor import investor_bp
    from routes.startup import startup_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(investor_bp, url_prefix='/investor')
    app.register_blueprint(startup_bp, url_prefix='/startup')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        from models.setting import Setting
        if not Setting.query.first():
            db.session.add(Setting(platform_fee_percentage=10.0))
            db.session.commit()
            
        from werkzeug.security import generate_password_hash
        if not User.query.filter_by(email='admin@fundgrow.com').first():
            admin = User(
                name='Admin',
                email='admin@fundgrow.com',
                password_hash=generate_password_hash('Admin@123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
""",
    "database.sql": """CREATE DATABASE IF NOT EXISTS fundgrow;
USE fundgrow;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    phone VARCHAR(20),
    role ENUM('investor', 'startup', 'admin') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    owner_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    goal_amount DECIMAL(15, 2) NOT NULL,
    raised_amount DECIMAL(15, 2) DEFAULT 0.00,
    category VARCHAR(50) NOT NULL,
    duration_days INT NOT NULL,
    image_path VARCHAR(255),
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform_fee_percentage DECIMAL(5, 2) NOT NULL DEFAULT 10.00
);

CREATE TABLE investments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    investor_id INT NOT NULL,
    project_id INT NOT NULL,
    percentage DECIMAL(5, 2) NOT NULL,
    investment_amount DECIMAL(15, 2) NOT NULL,
    platform_fee DECIMAL(15, 2) NOT NULL,
    net_amount DECIMAL(15, 2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (investor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    investor_id INT NOT NULL,
    project_id INT NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    platform_fee DECIMAL(15, 2) NOT NULL,
    transferred_amount DECIMAL(15, 2) NOT NULL,
    transaction_reference VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (investor_id) REFERENCES users(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

INSERT INTO settings (platform_fee_percentage) VALUES (10.00);
""",
    "models/__init__.py": """from flask_sqlalchemy import SQLAlchemy\n\ndb = SQLAlchemy()\n""",
    "models/user.py": """from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship('Project', backref='owner', lazy=True)
    investments = db.relationship('Investment', backref='investor', lazy=True)
""",
    "models/project.py": """from . import db
from datetime import datetime

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    goal_amount = db.Column(db.Numeric(15, 2), nullable=False)
    raised_amount = db.Column(db.Numeric(15, 2), default=0.00)
    category = db.Column(db.String(50), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    image_path = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    investments = db.relationship('Investment', backref='project', lazy=True)
""",
    "models/investment.py": """from . import db
from datetime import datetime

class Investment(db.Model):
    __tablename__ = 'investments'
    id = db.Column(db.Integer, primary_key=True)
    investor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    percentage = db.Column(db.Numeric(5, 2), nullable=False)
    investment_amount = db.Column(db.Numeric(15, 2), nullable=False)
    platform_fee = db.Column(db.Numeric(15, 2), nullable=False)
    net_amount = db.Column(db.Numeric(15, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
""",
    "models/transaction.py": """from . import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    investor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    platform_fee = db.Column(db.Numeric(15, 2), nullable=False)
    transferred_amount = db.Column(db.Numeric(15, 2), nullable=False)
    transaction_reference = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
""",
    "models/setting.py": """from . import db

class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    platform_fee_percentage = db.Column(db.Numeric(5, 2), nullable=False, default=10.00)
""",
    "routes/__init__.py": "",
    "routes/auth.py": """from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import abort

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
            
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password_hash=hashed_password, phone=phone, role=role)
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
""",
    "routes/main.py": """from flask import Blueprint, render_template, request
from models import db
from models.project import Project

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    category = request.args.get('category')
    query = Project.query.filter_by(status='approved')
    if category:
        query = query.filter_by(category=category)
    projects = query.order_by(Project.created_at.desc()).all()
    categories = db.session.query(Project.category).filter_by(status='approved').distinct().all()
    categories = [c[0] for c in categories]
    return render_template('index.html', projects=projects, categories=categories, selected_category=category)
    
@main_bp.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    if project.status != 'approved':
        return render_template('error.html', message="Project not available"), 404
    return render_template('project_detail.html', project=project)
""",
    "routes/investor.py": """from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db
from models.project import Project
from models.investment import Investment
from models.transaction import Transaction
from models.setting import Setting
from routes.auth import role_required
import uuid
import decimal

investor_bp = Blueprint('investor', __name__)

@investor_bp.route('/dashboard')
@login_required
@role_required('investor')
def dashboard():
    investments = Investment.query.filter_by(investor_id=current_user.id).order_by(Investment.created_at.desc()).all()
    total_invested = sum(inv.investment_amount for inv in investments)
    return render_template('investor/dashboard.html', investments=investments, total_invested=total_invested)

@investor_bp.route('/invest/<int:project_id>', methods=['GET', 'POST'])
@login_required
@role_required('investor')
def invest(project_id):
    project = Project.query.get_or_404(project_id)
    if project.status != 'approved':
        flash('Project not available for investment.', 'danger')
        return redirect(url_for('main.index'))
        
    setting = Setting.query.first()
    platform_fee_percentage = setting.platform_fee_percentage if setting else decimal.Decimal('10.00')
        
    if request.method == 'POST':
        percentage_str = request.form.get('percentage')
        if not percentage_str:
            flash('Invalid percentage', 'danger')
            return redirect(url_for('investor.invest', project_id=project.id))
            
        percentage = decimal.Decimal(percentage_str)
        if percentage <= 0 or percentage > 100:
            flash('Percentage must be between 1 and 100', 'danger')
            return redirect(url_for('investor.invest', project_id=project.id))
            
        agreement = request.form.get('agreement')
        if not agreement:
            flash('You must accept the agreement.', 'danger')
            return redirect(url_for('investor.invest', project_id=project.id))

        # Calculation
        investment_amount = project.goal_amount * (percentage / decimal.Decimal('100.00'))
        
        if (project.raised_amount + investment_amount) > project.goal_amount:
            val = project.goal_amount - project.raised_amount
            flash(f'Investment exceeds the remaining goal amount! Maximum allowed is ${val}.', 'warning')
            return redirect(url_for('investor.invest', project_id=project.id))

        # Show mock payment confirmation
        return render_template('investor/payment.html', 
                               project=project, 
                               percentage=percentage, 
                               investment_amount=investment_amount,
                               platform_fee_percentage=platform_fee_percentage)

    return render_template('investor/invest.html', project=project, platform_fee_percentage=platform_fee_percentage)

@investor_bp.route('/process_payment/<int:project_id>', methods=['POST'])
@login_required
@role_required('investor')
def process_payment(project_id):
    project = Project.query.get_or_404(project_id)
    percentage = decimal.Decimal(request.form.get('percentage'))
    
    setting = Setting.query.first()
    platform_fee_percentage = setting.platform_fee_percentage if setting else decimal.Decimal('10.00')
    
    investment_amount = project.goal_amount * (percentage / decimal.Decimal('100.00'))
    
    if (project.raised_amount + investment_amount) > project.goal_amount:
            flash('Investment exceeds the remaining goal amount!', 'warning')
            return redirect(url_for('investor.invest', project_id=project.id))
            
    platform_fee = investment_amount * (platform_fee_percentage / decimal.Decimal('100.00'))
    net_amount = investment_amount - platform_fee
    
    # Store investment
    inv = Investment(
        investor_id=current_user.id,
        project_id=project.id,
        percentage=percentage,
        investment_amount=investment_amount,
        platform_fee=platform_fee,
        net_amount=net_amount
    )
    db.session.add(inv)
    
    # Update project
    project.raised_amount += investment_amount
    
    # Store transaction
    txn_ref = str(uuid.uuid4())
    txn = Transaction(
        investor_id=current_user.id,
        project_id=project.id,
        amount=investment_amount,
        platform_fee=platform_fee,
        transferred_amount=net_amount,
        transaction_reference=txn_ref
    )
    db.session.add(txn)
    
    db.session.commit()
    
    flash('Payment successful! Investment recorded.', 'success')
    return render_template('investor/success.html', transaction=txn, project=project, net=net_amount)

@investor_bp.route('/history')
@login_required
@role_required('investor')
def history():
    transactions = Transaction.query.filter_by(investor_id=current_user.id).order_by(Transaction.created_at.desc()).all()
    return render_template('investor/history.html', transactions=transactions)
""",
    "routes/startup.py": """from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import db
from models.project import Project
from routes.auth import role_required
import os
from werkzeug.utils import secure_filename
import decimal

startup_bp = Blueprint('startup', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@startup_bp.route('/dashboard')
@login_required
@role_required('startup')
def dashboard():
    projects = Project.query.filter_by(owner_id=current_user.id).order_by(Project.created_at.desc()).all()
    total_raised = sum(p.raised_amount for p in projects)
    return render_template('startup/dashboard.html', projects=projects, total_raised=total_raised)

@startup_bp.route('/add_project', methods=['GET', 'POST'])
@login_required
@role_required('startup')
def add_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        goal_amount = decimal.Decimal(request.form.get('goal_amount'))
        category = request.form.get('category')
        duration_days = int(request.form.get('duration_days'))
        
        file = request.files.get('image')
        image_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{current_user.id}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name))
            image_path = unique_name
            
        new_project = Project(
            owner_id=current_user.id,
            name=name,
            description=description,
            goal_amount=goal_amount,
            category=category,
            duration_days=duration_days,
            image_path=image_path
        )
        db.session.add(new_project)
        db.session.commit()
        flash('Project submitted successfully! Waiting for admin approval.', 'success')
        return redirect(url_for('startup.dashboard'))
        
    return render_template('startup/add_project.html')
""",
    "routes/admin.py": """from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db
from models.project import Project
from models.user import User
from models.transaction import Transaction
from models.setting import Setting
from routes.auth import role_required
import decimal

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    projects_count = Project.query.count()
    users_count = User.query.filter(User.role != 'admin').count()
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(10).all()
    total_platform_fee = sum(t.platform_fee for t in Transaction.query.all())
    return render_template('admin/dashboard.html', 
                           projects_count=projects_count, 
                           users_count=users_count, 
                           transactions=transactions,
                           total_fee=total_platform_fee)

@admin_bp.route('/pending_projects')
@login_required
@role_required('admin')
def pending_projects():
    projects = Project.query.filter_by(status='pending').all()
    return render_template('admin/pending_projects.html', projects=projects)

@admin_bp.route('/published_projects')
@login_required
@role_required('admin')
def published_projects():
    projects = Project.query.filter_by(status='approved').all()
    return render_template('admin/published_projects.html', projects=projects)

@admin_bp.route('/project_action/<int:project_id>/<action>')
@login_required
@role_required('admin')
def project_action(project_id, action):
    project = Project.query.get_or_404(project_id)
    if action == 'approve':
        project.status = 'approved'
        flash('Project approved successfully.', 'success')
    elif action == 'reject':
        project.status = 'rejected'
        flash('Project rejected.', 'warning')
    db.session.commit()
    return redirect(url_for('admin.pending_projects'))

@admin_bp.route('/users')
@login_required
@role_required('admin')
def users_management():
    users = User.query.filter(User.role != 'admin').all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/transactions')
@login_required
@role_required('admin')
def all_transactions():
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
    return render_template('admin/transactions.html', transactions=transactions)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def settings():
    setting = Setting.query.first()
    if request.method == 'POST':
        new_fee = request.form.get('fee')
        try:
            fee_val = decimal.Decimal(new_fee)
            if fee_val < 0 or fee_val > 100:
                raise ValueError
            if not setting:
                setting = Setting(platform_fee_percentage=fee_val)
                db.session.add(setting)
            else:
                setting.platform_fee_percentage = fee_val
            db.session.commit()
            flash('Settings updated successfully.', 'success')
        except:
            flash('Invalid fee percentage. Must be 0-100.', 'danger')
            
    return render_template('admin/settings.html', setting=setting)
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Python setup 1 completed.")
