# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from models import db
from routes import main

# Flask Config
app = Flask(__name__)
app.config.from_object(Config)
# app.secret_key = 'a387dea9ba6b4303c98dbe5b7d0d0854'

# Register the routes
app.register_blueprint(main)

# Initialize database and login manager
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'main.login' # Redirect to login page if not logged in

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app.run(debug=True)