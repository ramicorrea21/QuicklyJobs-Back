from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
from flask_migrate import Migrate
from dotenv import load_dotenv  # Importa la función load_dotenv
import os

# Carga las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')  # Usa os.getenv para obtener el valor de la variable

db.init_app(app)
migrate = Migrate(app, db)

# Importa las rutas/endpoints después de inicializar la aplicación
from routes import *

if __name__ == "__main__":
    app.run(debug=True)