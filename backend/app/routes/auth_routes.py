import json
from flask import Blueprint, Response, request
from flask_jwt_extended import create_access_token

from .. import db
from ..models import StudentProfile, User

auth_api_blueprint = Blueprint('auth_api', __name__, url_prefix='/api')


@auth_api_blueprint.route('/login', methods=['POST'])
def login():
    """Аутентификация пользователя или подготовка к регистрации."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        response_data = {
            "status": "register",
            "email": email,
            "password": password
        }
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 200

    if not user.check_password(password):
        response_data = {'error': 'Invalid password'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 401

    access_token = create_access_token(identity=str(user.user_id))
    profile = user.profile
    profile_data = {
        "email": user.email,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "group_code": profile.group_code,
        "gender": profile.gender
    }
    response_data = {
        "access_token": access_token,
        "profile": profile_data
    }
    return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 200


@auth_api_blueprint.route('/register', methods=['POST'])
def register():
    """Регистрация нового пользователя."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    group_code = data.get('group_code')
    gender = ""
    language = ""

    if not all([email, password, first_name, last_name, group_code]):
        response_data = {'error': 'Missing required fields'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 400

    # Валидация пароля
    if len(password) < 8:
        response_data = {'error': 'Пароль должен содержать минимум 8 символов'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 400

    if User.query.filter_by(email=email).first():
        response_data = {'error': 'Email already exists'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 400

    student_profile = StudentProfile(
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        language=language,
        group_code=group_code,
    )
    db.session.add(student_profile)
    db.session.flush()

    user = User(email=email, profile_id=student_profile.profile_id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.user_id))
    profile_data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "group_code": group_code,
        "gender": gender
    }
    response_data = {
        "access_token": access_token,
        "profile": profile_data
    }
    return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 201
