from . import db

class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    platform_fee_percentage = db.Column(db.Numeric(5, 2), nullable=False, default=10.00)
