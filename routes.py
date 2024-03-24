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
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#populate db
user_path = os.path.join(os.path.dirname(__file__), "users.json")
profiles_path = os.path.join(os.path.dirname(__file__), "profiles.json")
services_path = os.path.join(os.path.dirname(__file__), "services.json")
requests_path = os.path.join(os.path.dirname(__file__), "requests.json")

smtp_address = os.getenv("SMTP_ADDRESS") 
smtp_port = os.getenv("SMTP_PORT") 
email_address = os.getenv("EMAIL_ADDRESS") 
email_password = os.getenv("EMAIL_PASSWORD") 

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

@app.route('/profile-population', methods=['GET'])
def profiles_population():
    with open('profiles.json', 'r') as file:  
        data = json.load(file)

    for profile_data in data:
        profile = Profile(
            user_id=profile_data['user_id'],
            first_name=profile_data['first_name'],
            last_name=profile_data['last_name'],
            description=profile_data['description'],
            phone=profile_data['phone'],
            available=profile_data['available'],
            city=profile_data['city'],
            country=profile_data['country'],
            profession=profile_data['profession'],
            category=profile_data['category'],
            avatar=profile_data['avatar'],
            company=profile_data['company'],
            role=profile_data['role'],
            experience=profile_data['experience'],
            hiring=profile_data['hiring'],
            looking_for=profile_data['looking_for']
        )
        db.session.add(profile)

    try:
        db.session.commit()
        return jsonify({"message": "Profiles populated successfully."}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 500

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
            remote = service['remote'],
            city = service['city'],
            country = service['country'],
            price_min = service['price_min'],
            price_max = service['price_max'],
            pictures = service['pictures'],
            avatar = service['avatar'],
            user_handle = service['user_handle'],
            profession = service['profession']
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
            profession = profile_info.profession,
            email = user.user_email
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
            profession = profile_info.profession,
            email = user.user_email
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

@app.route('/service/<int:id>', methods=['GET'])
def get_service_detail(id):
    service = Services.query.filter_by(id = id).one_or_none()
    if service is None:
        return jsonify({"error":"missing service"}), 404
    return jsonify(service.serialize()), 200


@app.route('/request/<int:id>', methods=['GET'])
def get_request_detail(id):
    request = Requests.query.filter_by(id = id).one_or_none()
    if request is None:
        return jsonify({"error":"missing service"}), 404
    return jsonify(request.serialize()), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_public_profile(user_id):
    user = Users.query.filter_by(id = user_id).one_or_none()
    if  user is None:
        return jsonify({"error":"profile not found"})
    
    return jsonify(user.serialize( ))

@app.route('/profile/<int:id>', methods=['GET'])
def get_profile(id):
    profile = Profile.query.filter_by(user_id = id).one_or_none()
    if profile is None:
        return jsonify({"error":"profile not found"}), 404
    return jsonify(profile.serialize()), 200

def send_email(subject, to, body):
    
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = 'notificationquicklyjobs@gmail.com'
    message["To"] = to

    html = '''
        <html>
        <body>
        ''' + body + '''   
        </body>
        </html>
    '''

    #crear los elemento MIME
    html_mime = MIMEText(html, 'html')

    #adjuntamos el código html al mensaje
    message.attach(html_mime)

    try:
        print("me ejecuto en el endpoint en enviar mensaje")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_address, 465, context=context) as server:
            server.login('notificationquicklyjobs@gmail.com', email_password)
            server.sendmail('notificationquicklyjobs@gmail.com', to, message.as_string())
            print("me ejecuto")
        return True
    except Exception as error:
        print(str(error))
        return False

def email_send(subject, recipient, message):
    message = f"Subject: {subject}\nTo: {recipient}\n{message}"
    try:
        server = smtplib.SMTP(smtp_address, 465)
        server.starttls()
        server.login('notificationquicklyjobs@gmail.com', email_password)
        server.sendmail('notificationquicklyjobs@gmail.com', recipient, message)
        server.quit()
        print('message has been sent')
        return True
    except Exception as error:
        print(error)
        print('This is the error capture')
        return False


@app.route('/sendemail', methods=['POST'])
def send_email_app():
    request_data = request.json
    print(request_data)
    
    # Verifica que todos los campos necesarios estén en el JSON
    required_fields = ["title", "phone", "email", "subject", "to", "to_name", "my_name"]
    for field in required_fields:
        if field not in request_data or not request_data[field]:
            return jsonify(f"Field {field} is missing or empty"), 400
    
    title = request_data["title"]
    phone = request_data["phone"]
    email = request_data["email"]
    subject = request_data["subject"]
    recipient = request_data["to"]
    to_name = request_data['to_name']
    my_name = request_data['my_name']

    # Aquí puedes construir tu mensaje HTML como lo necesites.
    email_message = f'''
<html>
    <head>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                color: #333;
            }}
            .container {{
                width: 80%;
                margin: auto;
                background-color: #f8f8f8;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                text-align: center;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            .footer {{
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                text-align: center;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Interested in Your Offer on QuicklyJobs</h2>
            </div>
            <p>Dear {to_name},</p>
            <p>I recently came across your offer titled "<strong>{title}</strong>" on QuicklyJobs, and I am very interested in learning more about this opportunity. I believe that my skills and experiences align well with the requirements you have posted, and I am eager to bring my contributions to the table.</p>
            
            <p>Please find my contact information below to coordinate a meeting where we can discuss this in further detail:</p>
            <p><strong>Phone:</strong> {phone}</p>
            <p><strong>Email:</strong> {email}</p>
            
            <p>I am looking forward to your response and hope to speak with you soon.</p>
            
            <p>Best regards,</p>
            <p>{my_name}</p>
            
            <div class="footer">
                <p>Thank you for considering my application.</p>
            </div>
        </div>
    </body>
</html>
'''
    
    result = send_email(subject, recipient, email_message)
    if result:
        return jsonify("Message has been sent"), 200
    else:
        return jsonify("Message failed"), 500

#edit service
#delete service
#post request
#edit request
#delete request    





