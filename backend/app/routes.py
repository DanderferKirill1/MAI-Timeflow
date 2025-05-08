from flask import Blueprint, jsonify, render_template, request, send_from_directory
from flask_jwt_extended import create_access_token, jwt_required

from . import db
from .models import StudentProfile, User  # , Course, Group

api_blueprint = Blueprint('api', __name__, url_prefix='/api')

frontend_blueprint = Blueprint('frontend', __name__)


@api_blueprint.route("/data", methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from Flask!"})


@api_blueprint.route('/register', methods=['POST'])
def register():
    """Регистрация нового пользователя."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    gender = data.get('gender')
    language = data.get('language')
    group_code = data.get('group_code')

    # Проверка обязательных полей
    if not all([email, password, first_name, last_name, group_code]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Проверка, существует ли пользователь
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    # Проверка, существует ли группа
    # group = Group.query.get(group_code)
    # if not group:
    #    return jsonify({'error': 'Invalid group_code'}), 404

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

    return jsonify({'message': 'User registered successfully'}), 201


@api_blueprint.route('/login', methods=['POST'])
def login():
    """Аутентификация пользователя и выдача JWT-токена."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    # group_code = data.get('group_code')

    # Поиск пользователя
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Проверка group_code
    # if user.profile.group_code != group_code:
    #    return jsonify({'error': 'Invalid group_code'}), 401

    # Генерация JWT-токена
    access_token = create_access_token(identity=str(user.user_id))
    return jsonify({'access_token': access_token}), 200


@api_blueprint.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """Защищённый эндпоинт, доступный только с JWT-токеном."""
    return jsonify({'message': 'This is a protected endpoint'}), 200


@frontend_blueprint.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@frontend_blueprint.route('/static/<path:filename>', methods=['GET'])
def static_files(filename):
    return send_from_directory("../../frontend/static", filename)


@frontend_blueprint.route('/assets/<path:filename>', methods=['GET'])
def assets_files(filename):
    return send_from_directory("../../frontend/assets", filename)
