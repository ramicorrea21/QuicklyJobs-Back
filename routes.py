from flask import jsonify, request
from app import app 
from models import db, Users, Profile, Services, Requests
import json
import os

user_path = os.path.join(os.path.dirname(__file__), "users.json")
profiles_path = os.path.join(os.path.dirname(__file__), "profiles.json")
services_path = os.path.join(os.path.dirname(__file__), "services.json")
requests_path = os.path.join(os.path.dirname(__file__), "requests.json")

@app.route("/user-population", methods=["GET"])
def user_population():
    with open(user_path, "r") as file:
        data = json.load(file)
        file.close
        
        for user in data:
            user = Users(
                user_handle=user['user_handle'],
                user_email=user['user_email'],
                password = user['password']
            )
            db.session.add(user)
        try:
            db.session.commit()
            return jsonify({"message":"users populated"})
        except Exception as error:
            db.session.rollback()
            return jsonify({"error":f"{error.args}"})

@app.route("/profiles-population", methods=["GET"])
def profiles_population():
    with open(profiles_path, "r") as file:
        data = json.load(file)
        file.close

    for profile in data:
        profile = Profile(
            user_id=profile['user_id'],
            first_name = profile['first_name'],
            last_name = profile['last_name'],
            description = profile['description'],
            phone = profile['phone'],
            location = profile['location'],
            address = profile['address'],
            profession = profile['profession'],
            category = profile['category']
        )
        db.session.add(profile)

    try:
        db.session.commit()
        return jsonify({"message":"profiles populated"})
    except Exception as error:
        db.session.rollback()
        return jsonify({"error":f"{error.args}"})

@app.route('/services-population', methods=["GET"])
def services_population():
    with open(services_path, "r") as file:
        data = json.load(file)
        file.close
    
    for service in data:
        service = Services(
            user_id = service['user_id'],
            title = service['title'],
            description = service['description'],
            category = service['category'],
            is_remote = service['is_remote'],
            location = service['location'],
            price_range = service['price_range']
        )
        db.session.add(service)
    try:
        db.session.commit()
        return jsonify({"message":"services populated"})
    except Exception as error:
        db.session.rollback()
        return jsonify({"error":f"{error.args}"})
    
@app.route('/requests-population', methods=["GET"])
def requests_population():
    with open(requests_path, "r") as file:
        data = json.load(file)
        file.close
    
    for request in data:
        request = Requests(
            user_id = request['user_id'],
            title = request['title'],
            description = request['description'],
            category = request['category'],
            is_remote = request['is_remote'],
            location = request['location'],
            price_range = request['price_range']
        )
        db.session.add(request)
    try:
        db.session.commit()
        return jsonify({"message":"requests populated"})
    except Exception as error:
        db.session.rollback()
        return jsonify({"error":f"{error.args}"})






