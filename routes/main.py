from flask import Blueprint, render_template, request
from flask_login import current_user
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

@main_bp.route('/about')
def about():
    return render_template('about.html')
    
@main_bp.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Allow admins to see any project
    # Allow owners to see their own project
    # Approved projects can be seen by everyone
    is_owner = current_user.is_authenticated and current_user.id == project.owner_id
    is_admin = current_user.is_authenticated and current_user.role == 'admin'
    
    if project.status != 'approved' and not is_admin and not is_owner:
        return render_template('error.html', message="Project not available"), 404
        
    from models.investment import Investment
    has_invested = False
    if current_user.is_authenticated and current_user.role == 'investor':
        has_invested = Investment.query.filter_by(investor_id=current_user.id, project_id=project.id).first() is not None
        
    return render_template('project_detail.html', project=project, is_owner=is_owner, is_admin=is_admin, has_invested=has_invested)

@main_bp.route('/project/<int:project_id>/document')
def download_document(project_id):
    project = Project.query.get_or_404(project_id)
    
    is_owner = current_user.is_authenticated and current_user.id == project.owner_id
    is_admin = current_user.is_authenticated and current_user.role == 'admin'
    
    has_invested = False
    if current_user.is_authenticated and current_user.role == 'investor':
        from models.investment import Investment
        has_invested = Investment.query.filter_by(investor_id=current_user.id, project_id=project.id).first() is not None
        
    if not (is_admin or is_owner or has_invested):
        # We also allow any logged in investor or admin to see the document per original logic
        if not (current_user.is_authenticated and current_user.role in ['investor', 'admin']):
            return "Unauthorized", 403
            
    if not project.document_path:
        return "No document available", 404
        
    from flask import send_from_directory, current_app
    # Wait, "apper not downloaded", if they want it TO download:
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], project.document_path, as_attachment=True)
