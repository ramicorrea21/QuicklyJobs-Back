from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_handle = db.Column(db.String(50), nullable=False, unique=True)
    user_email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    profile = db.relationship('Profile', backref='Users')
    services = db.relationship('Services', backref='Users')
    requests = db.relationship('Requests', backref='Users')

    def serialize(self):
        return{
            "id" : self.id,
            "user_handle" : self.user_handle,
            "user_email" : self.user_email,
        }

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    profession = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
        
    def serialize(self):
        return{
            "id" : self.id,
            "user_id" : self.user_id,
            "first_name" : self.first_name,
            "last_name": self.last_name,
            "description" : self.description,
            "phone" : self.phone,
            "location": self.location,
            "address" : self.address,
            "profession" : self.profession,
            "category" : self.category
        }

class Services(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    is_remote = db.Column(db.Boolean, nullable=False)
    location = db.Column(db.String(250), nullable=False)
    price_range = db.Column(db.String(100), nullable=False)

    def serliaze(self):
        return{
        "id" : self.id,
        "user_id" : self.user_id,
        "title": self.title,
        "description": self.description,
        "category": self.category,
        "is_remote": self.is_remote,
        "location": self.location,
        "price_range": self.price_range
        }
    
class Requests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    is_remote = db.Column(db.Boolean, nullable=False)
    location = db.Column(db.String(250), nullable=False)
    price_range = db.Column(db.String(100), nullable=False)

    def serliaze(self):
        return{
        "id" : self.id,
        "user_id" : self.user_id,
        "title": self.title,
        "description": self.description,
        "category": self.category,
        "is_remote": self.is_remote,
        "location": self.location,
        "price_range": self.price_range
        }
    