from flask import Blueprint, render_template, request, flash, redirect, url_for
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
    setting = Setting.query.first()
    return render_template('admin/dashboard.html', 
                           projects_count=projects_count, 
                           users_count=users_count, 
                           transactions=transactions,
                           total_fee=total_platform_fee,
                           setting=setting)

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

@admin_bp.route('/project_action/<int:project_id>/<action>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def project_action(project_id, action):
    project = Project.query.get_or_404(project_id)
    if action == 'approve':
        project.status = 'approved'
        flash('Project approved successfully.', 'success')
    elif action == 'reject':
        reason = request.form.get('reason') if request.method == 'POST' else None
        project.status = 'rejected'
        project.rejection_reason = reason or "No reason provided."
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
