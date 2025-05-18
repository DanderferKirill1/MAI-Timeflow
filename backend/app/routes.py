import json
from flask import Blueprint, Response, render_template, request, send_from_directory
from flask_jwt_extended import create_access_token, jwt_required

from . import db
from .models import StudentProfile, User  # , Course, Group

api_blueprint = Blueprint('api', __name__, url_prefix='/api')

frontend_blueprint = Blueprint('frontend', __name__)


@api_blueprint.route("/data", methods=['GET'])
def get_data():
    data = {"message": "Hello from Flask!"}
    return Response(json.dumps(data, ensure_ascii=False), mimetype='application/json'), 200


@api_blueprint.route('/login', methods=['POST'])
def login():
    """Аутентификация пользователя или подготовка к регистрации."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Поиск пользователя по email
    user = User.query.filter_by(email=email).first()

    if not user:
        # Пользователь не найден, возвращаем email и пароль для регистрации
        response_data = {
            "status": "register",
            "email": email,
            "password": password
        }
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 200

    # Проверка пароля
    if not user.check_password(password):
        response_data = {'error': 'Invalid password'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 401

    # Генерация JWT-токена
    access_token = create_access_token(identity=str(user.user_id))

    # Получение данных профиля
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


@api_blueprint.route('/register', methods=['POST'])
def register():
    """Регистрация нового пользователя."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    group_code = data.get('group_code')
    gender = None
    language = None

    # Проверка обязательных полей
    if not all([email, password, first_name, last_name, group_code]):
        response_data = {'error': 'Missing required fields'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 400

    # Проверка, существует ли пользователь
    if User.query.filter_by(email=email).first():
        response_data = {'error': 'Email already exists'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 400

    # Создание профиля студента
    student_profile = StudentProfile(
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        language=language,
        group_code=group_code,
    )
    db.session.add(student_profile)
    db.session.flush()  # Получаем profile_id

    # Создание пользователя
    user = User(email=email, profile_id=student_profile.profile_id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Генерация JWT-токена
    access_token = create_access_token(identity=str(user.user_id))

    # Данные профиля для ответа
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


@api_blueprint.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """Защищённый эндпоинт, доступный только с JWT-токеном."""
    response_data = {'message': 'This is a protected endpoint'}
    return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 200


@frontend_blueprint.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@frontend_blueprint.route('/static/<path:filename>', methods=['GET'])
def static_files(filename):
    return send_from_directory("../../public/static", filename)


@frontend_blueprint.route('/assets/<path:filename>', methods=['GET'])
def assets_files(filename):
    return send_from_directory("../../public/assets", filename)
