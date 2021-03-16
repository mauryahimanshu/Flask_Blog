from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

# Obtained via 'secrets' module , using token_hex(32) method, can use token_urlsafe(32)
app.config['SECRET_KEY'] = 'aeb76d8fed384db32cb23dff35e5a10587b64b7e0e5c5363ef35f3f5a23b5af9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskblog import routes