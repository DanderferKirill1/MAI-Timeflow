from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import UserSession, db
from datetime import datetime
import platform
import user_agents

@bp.route('/api/check-token', methods=['GET'])
@jwt_required()
def check_token():
    try:
        current_user = get_jwt_identity()
        return jsonify({'message': 'Token is valid', 'user': current_user}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 401

@bp.route('/api/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    current_user_id = get_jwt_identity()
    sessions = UserSession.query.filter_by(user_id=current_user_id).all()
    return jsonify([session.to_dict() for session in sessions])

@bp.route('/api/sessions/current', methods=['POST'])
@jwt_required()
def update_current_session():
    current_user_id = get_jwt_identity()
    user_agent = request.headers.get('User-Agent')
    ip_address = request.remote_addr
    
    # Получаем информацию об ОС из User-Agent
    ua = user_agents.parse(user_agent)
    os_info = f"{ua.os.family} {ua.os.version_string}"
    
    # Ищем существующую сессию для этого устройства
    session = UserSession.query.filter_by(
        user_id=current_user_id,
        user_agent=user_agent
    ).first()
    
    if session:
        # Обновляем время последней активности
        session.last_activity = datetime.utcnow()
    else:
        # Создаем новую сессию
        session = UserSession(
            user_id=current_user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            os_info=os_info
        )
        db.session.add(session)
    
    db.session.commit()
    return jsonify(session.to_dict()) 