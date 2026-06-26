from . import db
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

    investor = db.relationship('User')
    project = db.relationship('Project')

