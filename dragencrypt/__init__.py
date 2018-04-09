from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask.ext.bcrypt import Bcrypt
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.login import LoginManager, UserMixin, login_required
from flask import Flask
import sys
import dragencrypt_settings

# Error Codes
NO_CONFIGURATION_FILE = 1

# Flask App
app = Flask(__name__, static_url_path='/static/')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Password hashing
bcrypt = Bcrypt(app)

# Set download and upload directories
try:
    app.config['UPLOAD_FOLDER'] = dragencrypt_settings.UPLOAD_FOLDER
    app.config['DOWNLOAD_FOLDER'] = dragencrypt_settings.DOWNLOAD_FOLDER
    app.config['SQLALCHEMY_DATABASE_URI'] = dragencrypt_settings.DATABASE_URI
    app.secret_key = dragencrypt_settings.SECRET_KEY
except:
    print "Make sure that you have configured the server settings."
    print "Copy dragencrypt_settings.py.dev to dragencrypt_settings.py"
    sys.exit(NO_CONFIGURATION_FILE)

# Database
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
db = SQLAlchemy(app)

# Create tables for models
db.init_app(app)
db.create_all()

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

from dragencrypt.routes import *

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Base.metadata.create_all(bind=engine)
