from flask import jsonify, request
from app import app 
from models import db, Users, Profile, Services, Requests
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
import cloudinary.uploader as uploader

#populate db
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

#post user
#password security:
def set_password(password):
    return generate_password_hash(f"{password}")

def check_password(hash_password, password):
    return check_password_hash(hash_password, f"{password}")

#endpoint
@app.route('/post_user', methods=['POST'])
def post_user():
    data = request.json
    user_handle = data.get('user_handle')
    user_email = data.get('user_email')
    password = data.get('password')

    #validating if the user already exists
    if user_handle is None or user_email is None or password is None:
        return jsonify({"error":"bad request"}), 400
    
    handle = Users.query.filter_by(user_handle=user_handle).one_or_none()
    email = Users.query.filter_by(user_email = user_email). one_or_none()

    if handle is not None:
        return jsonify({"message":"username already exists"}), 400
    if email is not None:
        return jsonify({"message":"email already exists"}), 400
    
    #creating new user
    password = set_password(password)
    new_user = Users(
        user_handle = user_handle,
        user_email = user_email, 
        password = password
    )
    db.session.add(new_user)
    try:
        db.session.commit()
        return jsonify({"message": "user added correctly"}), 201
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": f"{error.args}"}), 500
    

#logintoken
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        user_email = data.get('user_email')
        password = data.get('password')

        #validate if the credentials are good
        user = Users.query.filter_by(user_email = user_email).one_or_none()
        if user is None or not check_password_hash(user.password, f'{password}'):
            return jsonify({'message': 'Invalid email or password'}), 400
    
        #if the credentials match, generate a login token
        token = create_access_token(
            identity={
                'email' : user.user_email,
                'id' : user.id
            }
        )
        return jsonify({'token': f"{token}"}), 200
    
    except Exception as error:
        return jsonify({"error":f"{error}"}), 500
    

#fetch user
    
@app.route('/fetch_user', methods=['GET'])
@jwt_required()
def fetch_user():
    user_id = get_jwt_identity()["id"]  
    user_data = Users.query.filter_by(id=user_id).one_or_none()
    profile_data = Profile.query.filter_by(user_id=user_id).one_or_none()

    if not user_data:
        return jsonify({"error": "User not found"}), 404

    user_serialized = user_data.serialize()
    profile_serialized = profile_data.serialize() if profile_data else None

    return jsonify({
        "user": user_serialized,
        "profile": profile_serialized
    }), 200


#post profile

@app.route('/post-profile', methods=['POST'])
@jwt_required()
def post_profile():
    user_id = get_jwt_identity()["id"]
    body_form = request.form
    body_file = request.files
    profile_exists = Profile.query.filter_by(user_id=user_id).one_or_none()

    if profile_exists:
        return jsonify({"error": "Profile already exists"}), 400

    try:

        avatar = body_file.get('avatar')

        result_avatar = uploader.upload(body_file.get("avatar"))
        avatar = result_avatar.get("secure_url")
        public_id = result_avatar.get("public_id")

        new_profile = Profile(
            user_id=user_id,
            first_name=body_form.get('first_name'),
            last_name=body_form.get('last_name'),
            description=body_form.get('description'),
            phone=body_form.get('phone'),
            available=body_form.get('available'),
            city=body_form.get('city'),
            country = body_form.get('country'),
            profession=body_form.get('profession'),
            category=body_form.get('category'),
            avatar = avatar,
            public_image_id = public_id,
            company = body_form.get('company'),
            role = body_form.get('role'),
            experience = body_form.get('experience'),
            hiring  = body_form.get('hiring'),
            looking_for = body_form.get('looking_for')
        )
        db.session.add(new_profile)
        db.session.commit()


        return jsonify(new_profile.serialize()), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Data integrity issue"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#update profile

@app.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()['id']
    body_form = request.form
    body_file = request.files
    profile_to_update = Profile.query.filter_by(user_id=user_id).first()

    if not profile_to_update:
        return jsonify({"error": "Profile not found"}), 404

    for field in ['first_name', 'last_name', 'description', 'phone', 'city', 'available', 'country', 'profession', 'category', 'company', 'role', 'experience', 'hiring', 'looking_for']:
        if field in body_form:
            setattr(profile_to_update, field, body_form[field])

    if 'avatar' in body_file and body_file['avatar']:
        try:
            result_avatar = uploader.upload(body_file.get("avatar"))
            profile_to_update.avatar = result_avatar.get("secure_url")
            profile_to_update.public_image_id = result_avatar.get("public_id")
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    try:
        db.session.commit()
        return jsonify(profile_to_update.serialize()), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 500


#post service
@app.route('/post-service', methods=['POST'])
@jwt_required()
def post_service():
    user_id = get_jwt_identity()['id']
    body_form = request.form
    body_file = request.files
    profile_info = Profile.query.filter_by(user_id=user_id).one_or_none()
    user = Users.query.filter_by(id = user_id).one_or_none()

    if profile_info is None  or profile_info.city is None is None:
        return jsonify({"error":"profile not complete"})

    try:

        pictures = body_file.get("images")
        result_image = uploader.upload(body_file.get("images"))
        pictures = result_image.get("secure_url")
        public_image_id = result_image.get("public_id")

        new_service = Services(
            user_id = user_id,
            title = body_form.get('title'),
            description = body_form.get('description'),
            category = body_form.get('category'),
            remote = body_form.get("remote"),
            city = profile_info.city,
            country = profile_info.country,
            price_min = body_form.get('price_min'),
            price_max = body_form.get('price_max'),
            pictures = pictures,
            public_image_id = public_image_id,
            avatar = profile_info.avatar,
            user_handle = user.user_handle,
            profession = profile_info.profession
        )

        db.session.add(new_service)
        db.session.commit()
        return jsonify(new_service.serialize()), 201
    
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Data integrity issue"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/post-request', methods=['POST'])
@jwt_required()
def post_request():
    user_id = get_jwt_identity()['id']
    body_form = request.form
    body_file = request.files
    profile_info = Profile.query.filter_by(user_id=user_id).one_or_none()
    user = Users.query.filter_by(id = user_id).one_or_none()

    if profile_info is None or profile_info.city is None  is None:
        return jsonify({"error":"profile not complete"})

    try:

        pictures = body_file.get("images")
        result_image = uploader.upload(body_file.get("images"))
        pictures = result_image.get("secure_url")
        public_image_id = result_image.get("public_id")

        new_request = Requests(
            user_id = user_id,
            title = body_form.get('title'),
            description = body_form.get('description'),
            category = body_form.get('category'),
            remote = body_form.get('remote'),
            city = profile_info.city,
            country = profile_info.country,
            price_min = body_form.get('price_min'),
            price_max = body_form.get('price_max'),
            pictures = pictures,
            public_image_id = public_image_id,
            avatar = profile_info.avatar,
            user_handle = user.user_handle,
            profession = profile_info.profession
        )
        
        db.session.add(new_request)
        db.session.commit()
        return jsonify(new_request.serialize()), 201
    
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Data integrity issue"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#get all services
@app.route('/services', methods=['GET'])
def get_services():
    services = Services.query.all()
    return jsonify(list(map(lambda service: service.serialize(), services)))

@app.route('/requests', methods=['GET'])
def get_requests():
    requests = Requests.query.all()
    return jsonify(list(map(lambda request: request.serialize(), requests)))

@app.route('/service/<int:user_id>/<int:id>', methods=['GET'])
def get_service_detail(user_id, id):
    service = Services.query.filter_by(id = id).one_or_none()
    profile = Profile.query.filter_by(user_id = user_id).one_or_none()

    if service is None or profile is None:
        return jsonify({"error":"missing service"}), 404
    return jsonify(service.serialize(), profile.serialize()), 200


@app.route('/request/<int:user_id>/<int:id>', methods=['GET'])
def get_request_detail(user_id, id):
    request = Requests.query.filter_by(id = id).one_or_none()
    profile = Profile.query.filter_by(user_id = user_id).one_or_none()

    if request is None or profile is None:
        return jsonify({"error":"missing service"}), 404
    return jsonify(request.serialize(), profile.serialize()), 200

@app.route('/publicprofile/<int:user_id>', methods=['GET'])
def get_public_profile(user_id):
    profile = Profile.query.filter_by(user_id = user_id).one_or_none()
    user = Users.query.filter_by(id = user_id).one_or_none()
    if profile is None or user is None:
        return jsonify({"error":"profile not found"})
    
    return jsonify(profile.serialize(), user.serialize( ))




#edit service
#delete service
#post request
#edit request
#delete request    





