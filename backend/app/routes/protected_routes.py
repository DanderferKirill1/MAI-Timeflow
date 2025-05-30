import json
from flask import Blueprint, Response, request
from flask_jwt_extended import get_jwt_identity, jwt_required, unset_jwt_cookies
from .. import db
from ..models import User, UserSession, Notification, NotificationSettings
from datetime import datetime
import platform
from user_agents import parse

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
    try:
        user_id = get_jwt_identity()
        print(f"User ID from token: {user_id}")  # Отладочная информация
        
        data = request.get_json()
        print(f"Request data: {data}")  # Отладочная информация
        
        if not data:
            return Response(
                json.dumps({'error': 'No data provided'}, ensure_ascii=False),
                mimetype='application/json',
                status=400
            )

        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            return Response(
                json.dumps({'error': 'Old and new passwords are required'}, ensure_ascii=False),
                mimetype='application/json',
                status=400
            )

        # Валидация нового пароля
        if len(new_password) < 8:
            return Response(
                json.dumps({'error': 'Новый пароль должен содержать минимум 8 символов'}, ensure_ascii=False),
                mimetype='application/json',
                status=400
            )

        user = User.query.get(user_id)
        print(f"Found user: {user}")  # Отладочная информация
        
        if not user:
            return Response(
                json.dumps({'error': 'User not found'}, ensure_ascii=False),
                mimetype='application/json',
                status=404
            )

        # Проверяем текущий пароль
        is_valid = user.check_password(old_password)
        print(f"Password check result: {is_valid}")  # Отладочная информация
        
        if not is_valid:
            return Response(
                json.dumps({'error': 'Invalid old password'}, ensure_ascii=False),
                mimetype='application/json',
                status=401
            )

        user.set_password(new_password)
        db.session.commit()
        print("Password updated successfully")  # Отладочная информация

        return Response(
            json.dumps({'message': 'Password updated successfully'}, ensure_ascii=False),
            mimetype='application/json',
            status=200
        )
    except Exception as e:
        print(f"Error in change_password: {str(e)}")  # Отладочная информация
        db.session.rollback()
        return Response(
            json.dumps({'error': str(e)}, ensure_ascii=False),
            mimetype='application/json',
            status=500
        )


@protected_api_blueprint.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Логаут пользователя (удаление JWT с клиента)."""
    response = Response(json.dumps({'message': 'Logged out successfully'}), mimetype='application/json', status=200)
    unset_jwt_cookies(response)
    return response


@protected_api_blueprint.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Получение данных профиля пользователя."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        response_data = {'error': 'User not found'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json', status=404)
    
    profile = user.profile
    profile_data = {
        "email": user.email,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "group_code": profile.group_code,
        "gender": profile.gender,
        "language": profile.language
    }
    
    return Response(json.dumps(profile_data, ensure_ascii=False), mimetype='application/json', status=200)


@protected_api_blueprint.route('/check-token', methods=['GET'])
@jwt_required()
def check_token():
    """Проверка валидности JWT токена."""
    try:
        # Если токен валиден, get_jwt_identity() вернет user_id
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return Response(
                json.dumps({'error': 'User not found'}, ensure_ascii=False),
                mimetype='application/json',
                status=401
            )
            
        return Response(
            json.dumps({'valid': True}, ensure_ascii=False),
            mimetype='application/json',
            status=200
        )
    except Exception as e:
        return Response(
            json.dumps({'error': str(e)}, ensure_ascii=False),
            mimetype='application/json',
            status=401
        )


@protected_api_blueprint.route('/sessions/current', methods=['POST'])
@jwt_required()
def update_current_session():
    """Обновление текущей сессии пользователя."""
    try:
        user_id = get_jwt_identity()
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.remote_addr
        
        # Получаем информацию об ОС
        ua = parse(user_agent)
        os_info = f"{ua.os.family} {ua.os.version_string}"
        
        # Ищем существующую сессию
        session = UserSession.query.filter_by(
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address
        ).first()
        
        if session:
            # Обновляем время последней активности
            session.last_activity = datetime.utcnow()
        else:
            # Создаем новую сессию
            session = UserSession(
                user_id=user_id,
                user_agent=user_agent,
                ip_address=ip_address,
                os_info=os_info,
                last_activity=datetime.utcnow()
            )
            db.session.add(session)
        
        db.session.commit()
        
        return Response(
            json.dumps(session.to_dict(), ensure_ascii=False),
            mimetype='application/json',
            status=200
        )
    except Exception as e:
        return Response(
            json.dumps({'error': str(e)}, ensure_ascii=False),
            mimetype='application/json',
            status=500
        )


@protected_api_blueprint.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """Получение всех сессий пользователя."""
    try:
        user_id = get_jwt_identity()
        sessions = UserSession.query.filter_by(user_id=user_id).all()
        
        sessions_data = [session.to_dict() for session in sessions]
        
        return Response(
            json.dumps(sessions_data, ensure_ascii=False),
            mimetype='application/json',
            status=200
        )
    except Exception as e:
        return Response(
            json.dumps({'error': str(e)}, ensure_ascii=False),
            mimetype='application/json',
            status=500
        )


@protected_api_blueprint.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Получение уведомлений пользователя."""
    try:
        user_id = get_jwt_identity()
        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
        
        notifications_data = [notification.to_dict() for notification in notifications]
        
        return Response(
            json.dumps(notifications_data, ensure_ascii=False),
            mimetype='application/json',
            status=200
        )
    except Exception as e:
        print(f"Ошибка при получении уведомлений: {str(e)}")
        return Response(
            json.dumps({'error': str(e)}, ensure_ascii=False),
            mimetype='application/json',
            status=500
        )


@protected_api_blueprint.route('/notifications', methods=['POST'])
@jwt_required()
def create_notification():
    """Создание нового уведомления."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Проверяем настройки уведомлений пользователя
        settings = NotificationSettings.query.filter_by(user_id=user_id).first()
        if not settings:
            settings = NotificationSettings(user_id=user_id)
            db.session.add(settings)
            db.session.commit()
        
        # Если уведомления отключены, не создаем их
        if data.get('type') == 'sync' and not settings.push_notifications:
            return Response(
                json.dumps({'message': 'Notifications disabled'}, ensure_ascii=False),
                mimetype='application/json',
                status=200
            )
        
        notification = Notification(
            user_id=user_id,
            type=data.get('type', 'sync'),
            subject_name=data.get('subject_name', ''),
            message=data.get('message', ''),
            created_at=datetime.utcnow(),
            is_read=False
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return Response(
            json.dumps(notification.to_dict(), ensure_ascii=False),
            mimetype='application/json',
            status=201
        )
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при создании уведомления: {str(e)}")
        return Response(
            json.dumps({'error': str(e)}, ensure_ascii=False),
            mimetype='application/json',
            status=500
        )


@protected_api_blueprint.route('/notification-settings', methods=['GET'])
@jwt_required()
def get_notification_settings():
    """Получение настроек уведомлений пользователя."""
    try:
        user_id = get_jwt_identity()
        settings = NotificationSettings.query.filter_by(user_id=user_id).first()
        
        if not settings:
            settings = NotificationSettings(user_id=user_id)
            db.session.add(settings)
            db.session.commit()
        
        return Response(
            json.dumps(settings.to_dict(), ensure_ascii=False),
            mimetype='application/json',
            status=200
        )
    except Exception as e:
        return Response(
            json.dumps({'error': str(e)}, ensure_ascii=False),
            mimetype='application/json',
            status=500
        )


@protected_api_blueprint.route('/notification-settings', methods=['PUT'])
@jwt_required()
def update_notification_settings():
    """Обновление настроек уведомлений пользователя."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        settings = NotificationSettings.query.filter_by(user_id=user_id).first()
        if not settings:
            settings = NotificationSettings(user_id=user_id)
            db.session.add(settings)
        
        if 'schedule_changes' in data:
            settings.schedule_changes = data['schedule_changes']
        if 'lesson_reminders' in data:
            settings.lesson_reminders = data['lesson_reminders']
        if 'reminder_time' in data:
            settings.reminder_time = data['reminder_time']
        if 'push_notifications' in data:
            settings.push_notifications = data['push_notifications']
        if 'email_notifications' in data:
            settings.email_notifications = data['email_notifications']
        if 'telegram_notifications' in data:
            settings.telegram_notifications = data['telegram_notifications']
        
        db.session.commit()
        
        return Response(
            json.dumps(settings.to_dict(), ensure_ascii=False),
            mimetype='application/json',
            status=200
        )
    except Exception as e:
        db.session.rollback()
        return Response(
            json.dumps({'error': str(e)}, ensure_ascii=False),
            mimetype='application/json',
            status=500
        )


@protected_api_blueprint.route('/notifications/<int:notification_id>/read', methods=['PUT', 'OPTIONS'])
@jwt_required()
def mark_notification_as_read(notification_id):
    """Отметка уведомления как прочитанного."""
    if request.method == 'OPTIONS':
        return Response(status=200)
        
    try:
        user_id = get_jwt_identity()
        notification = Notification.query.filter_by(
            notification_id=notification_id,
            user_id=user_id
        ).first()
        
        if not notification:
            return Response(
                json.dumps({'error': 'Notification not found'}, ensure_ascii=False),
                mimetype='application/json',
                status=404
            )
        
        notification.is_read = True
        db.session.commit()
        
        return Response(
            json.dumps({'message': 'Notification marked as read'}, ensure_ascii=False),
            mimetype='application/json',
            status=200
        )
    except Exception as e:
        db.session.rollback()
        return Response(
            json.dumps({'error': str(e)}, ensure_ascii=False),
            mimetype='application/json',
            status=500
        )
