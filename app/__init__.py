# app/__init__.py
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.extensions import db, migrate, login_manager  # Assuming these are in app/extensions.py

def create_app():
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    from app.tutor import tutor as tutor_blueprint
    app.register_blueprint(tutor_blueprint, url_prefix='/tutor')
    
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403
    
    # Seed the default admin user.
    with app.app_context():
        from app.models import User
        admin_email = "admin@gmail.com"
        admin_password = "admin"
        try:
            # Try executing a simple query that references the new columns.
            # If these columns do not exist yet, this will raise an exception.
            db.engine.execute("SELECT first_name, last_name FROM user LIMIT 1")
            # If the query succeeds, then check for the admin user.
            admin_user = User.query.filter_by(email=admin_email).first()
            if not admin_user:
                new_user = User(first_name="Admin", last_name="User", email=admin_email, role="admin")
                new_user.set_password(admin_password)
                db.session.add(new_user)
                db.session.commit()
                app.logger.info("Created default admin user: %s", admin_email)
        except Exception as e:
            # If the columns don't exist (or another error occurs), skip seeding.
            app.logger.info("Skipping admin seeding: %s", e)
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
