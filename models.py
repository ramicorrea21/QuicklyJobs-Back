from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_handle = db.Column(db.String(50), nullable=False, unique=True)
    user_email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
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
    phone = db.Column(db.String(20), nullable=False)
    available = db.Column(db.String(250), nullable=False)
    city = db.Column(db.String(250), nullable=False)
    country = db.Column(db.String(250), nullable=False)
    profession = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(250), nullable=True, unique=False)
    public_image_id = db.Column(db.String(100), unique=False)
    company = db.Column(db.String(250), unique=False)
    role = db.Column(db.String(250), unique=False)
    experience = db.Column(db.String(250), unique=False)
    hiring = db.Column(db.String(3), unique=False)
    looking_for = db.Column(db.String(3), unique=False)
        
    def serialize(self):
        return{
            "id" : self.id,
            "user_id" : self.user_id,
            "first_name" : self.first_name,
            "last_name": self.last_name,
            "description" : self.description,
            "phone" : self.phone,
            "available" : self.available,
            "city" : self.city,
            "country": self.country,
            "profession" : self.profession,
            "category" : self.category,
            "avatar": self.avatar,
            "company" : self.company,
            "role": self.role,
            "experience" : self.experience,
            "hiring": self.hiring,
            "looking_for" : self.looking_for
        }

class Services(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    remote = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(250), nullable=False)
    country = db.Column(db.String(250), nullable=False)
    price_min = db.Column(db.String(100), nullable=False)
    price_max = db.Column(db.String(100), nullable=False)
    pictures = db.Column(db.String(250), nullable=False)
    public_image_id = db.Column(db.String(100), unique=False)
    avatar = db.Column(db.String(250), unique=False, nullable=False)
    user_handle = db.Column(db.String(50), unique=False, nullable=False)
    profession = db.Column(db.String(250), unique=False, nullable=False)
    email = db.Column(db.String(250), unique=False, nullable=False)

    def serialize(self):
        return{
        "id" : self.id,
        "user_id" : self.user_id,
        "title": self.title,
        "description": self.description,
        "category": self.category,
        "is_remote": self.remote,
        "city" : self.city,
        "country": self.country,
        "price_min": self.price_min,
        "price_max": self.price_max,
        "pictures": self.pictures,
        "avatar": self.avatar,
        "user_handle": self.user_handle,
        "profession" : self.profession,
        "email" : self.email
        }
    
class Requests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    remote = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(250), nullable=False)
    country = db.Column(db.String(250), nullable=False)
    price_min = db.Column(db.String(100), nullable=False)
    price_max = db.Column(db.String(100), nullable=False)
    pictures = db.Column(db.String(250), nullable=False)
    public_image_id = db.Column(db.String(100), unique=False)
    avatar = db.Column(db.String(250), unique=False, nullable=False)
    user_handle = db.Column(db.String(50), unique=False, nullable=False)
    profession = db.Column(db.String(250), unique=False, nullable=False)
    email = db.Column(db.String(250), unique=False, nullable=False)

    def serialize(self):
        return{
        "id" : self.id,
        "user_id" : self.user_id,
        "title": self.title,
        "description": self.description,
        "category": self.category,
        "remote": self.remote,
        "city" : self.city,
        "country": self.country,
        "price_min": self.price_min,
        "price_max": self.price_max,
        "pictures": self.pictures,
        "avatar": self.avatar,
        "user_handle": self.user_handle,
        "profession" : self.profession,
        "email" : self.email
        }
    
    