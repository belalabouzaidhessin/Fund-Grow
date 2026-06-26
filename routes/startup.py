from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import db
from models.project import Project
from routes.auth import role_required
import os
from werkzeug.utils import secure_filename
import decimal

startup_bp = Blueprint('startup', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_DOC_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_doc(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOC_EXTENSIONS

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
        phone_number = request.form.get('phone_number')

        est_cost_str = request.form.get('est_cost')
        exp_revenue_str = request.form.get('exp_revenue')
        target_market = request.form.get('target_market')
        
        # Check feasibility study presence
        est_cost = decimal.Decimal(est_cost_str) if est_cost_str else None
        exp_revenue = decimal.Decimal(exp_revenue_str) if exp_revenue_str else None
        
        status = 'pending'
        rejection_reason = None
        if not est_cost or not exp_revenue or not target_market:
            status = 'rejected'
            rejection_reason = 'Automatically rejected: Missing incomplete feasibility study.'
        
        
        file = request.files.get('image')
        image_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{current_user.id}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name))
            image_path = unique_name
            
        doc_file = request.files.get('document')
        document_path = None
        if doc_file and allowed_doc(doc_file.filename):
            doc_filename = secure_filename(doc_file.filename)
            doc_unique_name = f"doc_{current_user.id}_{doc_filename}"
            doc_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], doc_unique_name))
            document_path = doc_unique_name
            
        logo_file = request.files.get('logo')
        logo_path = None
        if logo_file and allowed_file(logo_file.filename):
            logo_filename = secure_filename(logo_file.filename)
            logo_unique_name = f"logo_{current_user.id}_{logo_filename}"
            logo_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], logo_unique_name))
            logo_path = logo_unique_name
            
        new_project = Project(
            owner_id=current_user.id,
            name=name,
            description=description,
            goal_amount=goal_amount,
            category=category,
            duration_days=duration_days,
            image_path=image_path,
            document_path=document_path,
            logo_path=logo_path,
            phone_number=phone_number,
            est_cost=est_cost,
            exp_revenue=exp_revenue,
            target_market=target_market,
            status=status,
            rejection_reason=rejection_reason
        )
        db.session.add(new_project)
        db.session.commit()
        if status == 'rejected':
            flash('Project rejected automatically due to incomplete feasibility study.', 'danger')
        else:
            flash('Project submitted successfully! Waiting for admin approval.', 'success')
        return redirect(url_for('startup.dashboard'))
        
    return render_template('startup/add_project.html')

@startup_bp.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
@role_required('startup')
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.owner_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('startup.dashboard'))
    
    if request.method == 'POST':
        project.name = request.form.get('name')
        project.description = request.form.get('description')
        project.goal_amount = decimal.Decimal(request.form.get('goal_amount'))
        project.category = request.form.get('category')
        project.duration_days = int(request.form.get('duration_days'))
        project.phone_number = request.form.get('phone_number')
        
        est_cost_str = request.form.get('est_cost')
        exp_revenue_str = request.form.get('exp_revenue')
        project.target_market = request.form.get('target_market')
        
        if est_cost_str:
            project.est_cost = decimal.Decimal(est_cost_str)
        if exp_revenue_str:
            project.exp_revenue = decimal.Decimal(exp_revenue_str)
            
        # Reset status for re-approval
        project.status = 'pending'
        project.rejection_reason = None
        
        # Check files
        image_file = request.files.get('image')
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            unique_name = f"edit_{current_user.id}_{filename}"
            image_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name))
            project.image_path = unique_name
            
        doc_file = request.files.get('document')
        if doc_file and allowed_doc(doc_file.filename):
            doc_filename = secure_filename(doc_file.filename)
            doc_unique_name = f"doc_edit_{current_user.id}_{doc_filename}"
            doc_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], doc_unique_name))
            project.document_path = doc_unique_name
            
        logo_file = request.files.get('logo')
        if logo_file and allowed_file(logo_file.filename):
            logo_filename = secure_filename(logo_file.filename)
            logo_unique_name = f"logo_edit_{current_user.id}_{logo_filename}"
            logo_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], logo_unique_name))
            project.logo_path = logo_unique_name
            
        db.session.commit()
        flash('Project updated successfully and sent for re-approval.', 'success')
        return redirect(url_for('startup.dashboard'))
        
    return render_template('startup/edit_project.html', project=project)

@startup_bp.route('/withdraw/<int:project_id>', methods=['POST'])
@login_required
@role_required('startup')
def withdraw_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.owner_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('startup.dashboard'))
    
    # 2000 EGP fee policy
    if project.status == 'pending' or project.status == 'approved':
        project.status = 'rejected'
        project.rejection_reason = 'Withdrawn by owner. A fee of 2000 EGP has been applied for document retrieval and review processing.'
        db.session.commit()
        flash('Project documents withdrawn. A fee of 2000 EGP has been charged to your account.', 'warning')
    else:
        flash('Cannot withdraw this project.', 'danger')
        
    return redirect(url_for('startup.dashboard'))
