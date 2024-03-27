from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
from flask_migrate import Migrate
from dotenv import load_dotenv 
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)  
jwt = JWTManager(app)
CORS(app)

db.init_app(app)
migrate = Migrate(app, db)

from routes import *

if __name__ == "__main__":
    app.run(debug=True)
