from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os,sys

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///database.db')
session = Session(engine)

DIR_ROOT = os.path.dirname(sys.argv[0])
UPLOAD_FOLDER = 'uploads'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'toto'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)



