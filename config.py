import os

class Config:
    SECRET_KEY = 'super-secret-fundgrow-key-2026'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/fundgrow'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
