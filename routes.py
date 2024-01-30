from flask import jsonify, request
from app import app 
from models import db, Users  

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/users', methods=['GET'])
def obtener_usuarios():
    usuarios = Users.query.all()
    return jsonify(list(map(lambda usr : usr.serialize(), usuarios)))

#desarrollar api 

