from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_handle = db.Column(db.String(50), nullable=False, unique=True)
    user_email = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    user_lastname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def serialize(self):
        return{
            "id" : self.id,
            "user_handle" : self.user_handle,
            "user_email" : self.user_email,
            "user_name" : self.user_name,
            "user_lastname" : self.user_lastname,
        }
#terminar de desarrollar mis models