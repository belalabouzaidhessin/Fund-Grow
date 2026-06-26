from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db
from models.project import Project
from models.user import User
from models.message import Message
from models.investment import Investment

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/<int:project_id>/<int:other_user_id>', methods=['GET', 'POST'])
@login_required
def project_chat(project_id, other_user_id):
    project = Project.query.get_or_404(project_id)
    other_user = User.query.get_or_404(other_user_id)
    
    is_owner = current_user.id == project.owner_id
    has_invested = False
    
    if current_user.role == 'investor':
        has_invested = Investment.query.filter_by(investor_id=current_user.id, project_id=project.id).first() is not None
        if not has_invested:
            flash("You must invest in this project first to unlock direct chat.", "warning")
            return redirect(url_for('investor.invest', project_id=project.id))
            
    if not is_owner and not has_invested:
        flash("You are not authorized to view this chat.", "danger")
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            msg = Message(
                project_id=project.id,
                sender_id=current_user.id,
                receiver_id=other_user_id,
                content=content
            )
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for('chat.project_chat', project_id=project.id, other_user_id=other_user_id))
            
    # Mark messages as read
    unread_msgs = Message.query.filter_by(
        project_id=project.id,
        sender_id=other_user_id,
        receiver_id=current_user.id,
        is_read=False
    ).all()
    if unread_msgs:
        for um in unread_msgs:
            um.is_read = True
        db.session.commit()
        
    messages = Message.query.filter(
        Message.project_id == project.id,
        ((Message.sender_id == current_user.id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    return render_template('chat/room.html', project=project, other_user=other_user, messages=messages)

@chat_bp.route('/project/<int:project_id>')
@login_required
def project_chat_list(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.id != project.owner_id:
        flash("Only the project owner can view this list.", "danger")
        return redirect(url_for('main.index'))
        
    investments = Investment.query.filter_by(project_id=project.id).all()
    investor_ids = list(set([i.investor_id for i in investments]))
    investors = User.query.filter(User.id.in_(investor_ids)).all() if investor_ids else []
    
    return render_template('chat/list.html', project=project, investors=investors)

@chat_bp.route('/inbox')
@login_required
def inbox():
    from sqlalchemy import or_
    msgs = Message.query.filter(or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id)).order_by(Message.created_at.desc()).all()
    
    conversations = {}
    for m in msgs:
        other_user = m.sender if m.receiver_id == current_user.id else m.receiver
        key = (m.project_id, other_user.id)
        if key not in conversations:
            conversations[key] = {
                'project': m.project,
                'other_user': other_user,
                'last_message': m,
                'unread': 0
            }
        
        if m.receiver_id == current_user.id and not m.is_read:
            conversations[key]['unread'] += 1
            
    sorted_convos = sorted(conversations.values(), key=lambda x: x['last_message'].created_at, reverse=True)
    return render_template('chat/inbox.html', conversations=sorted_convos)
