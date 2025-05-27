import json
from flask import Blueprint, Response, request
from flask_jwt_extended import get_jwt_identity, jwt_required, unset_jwt_cookies
from .. import db
from ..models import User

protected_api_blueprint = Blueprint('protected_api', __name__, url_prefix='/api')


@protected_api_blueprint.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """Защищённый эндпоинт, доступный только с JWT-токеном."""
    response_data = {'message': 'This is a protected endpoint'}
    return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json', status=200)


@protected_api_blueprint.route('/profile/edit', methods=['PUT'])
@jwt_required()
def edit_profile():
    """Обновление данных профиля пользователя."""
    user_id = get_jwt_identity()
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    group_code = data.get('group_code')
    gender = data.get('gender')

    user = User.query.get(user_id)
    if not user:
        response_data = {'error': 'User not found'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json', status=404)

    profile = user.profile
    if first_name:
        profile.first_name = first_name
    if last_name:
        profile.last_name = last_name
    if group_code:
        profile.group_code = group_code
    if gender:
        profile.gender = gender

    db.session.commit()
    info = User.query.filter_by(user_id=user_id).first()
    print(info)
    profile_data = {
        "email": user.email,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "group_code": profile.group_code,
        "gender": profile.gender
    }
    response_data = {'message': 'Profile updated', 'profile': profile_data}
    return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json', status=200)


@protected_api_blueprint.route('/profile/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Смена пароля пользователя."""
    user_id = get_jwt_identity()
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        response_data = {'error': 'Old and new passwords are required'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json', status=400)

    user = User.query.get(user_id)
    if not user or not user.check_password(old_password):
        response_data = {'error': 'Invalid old password'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json', status=401)

    user.set_password(new_password)
    db.session.commit()
    response_data = {'message': 'Password updated successfully'}
    return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json', status=200)


@protected_api_blueprint.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Логаут пользователя (удаление JWT с клиента)."""
    response = Response(json.dumps({'message': 'Logged out successfully'}), mimetype='application/json', status=200)
    unset_jwt_cookies(response)
    return response
