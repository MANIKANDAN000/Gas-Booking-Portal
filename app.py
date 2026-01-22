from flask import Flask
from config import Config
from extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.user import user_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        from models import User
        admin = User.query.filter_by(email='admin@gasbooking.com').first()
        if not admin:
            admin = User(
                name='Admin',
                email='admin@gasbooking.com',
                phone='9999999999',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
