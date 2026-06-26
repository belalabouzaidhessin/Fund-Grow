from . import db
from datetime import datetime

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    goal_amount = db.Column(db.Numeric(15, 2), nullable=False)
    raised_amount = db.Column(db.Numeric(15, 2), default=0.00)
    est_cost = db.Column(db.Numeric(15, 2))
    exp_revenue = db.Column(db.Numeric(15, 2))
    target_market = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    image_path = db.Column(db.String(255))
    document_path = db.Column(db.String(255))
    logo_path = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    investments = db.relationship('Investment', backref='project', lazy=True)
