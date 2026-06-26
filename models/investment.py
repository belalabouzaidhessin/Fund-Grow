from . import db
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
