import os
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
    from routes.chatbot import chatbot_bp
    from routes.chat import chat_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(investor_bp, url_prefix='/investor')
    app.register_blueprint(startup_bp, url_prefix='/startup')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    csrf.exempt(chatbot_bp)
    app.register_blueprint(chat_bp, url_prefix='/chat')

    @app.context_processor
    def inject_unread_messages():
        from flask_login import current_user
        from models.message import Message
        unread_count = 0
        if current_user.is_authenticated:
            unread_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
        return dict(unread_count=unread_count)

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
