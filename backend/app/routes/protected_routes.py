import json
from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

protected_api_blueprint = Blueprint('protected_api', __name__, url_prefix='/api')  # Уникальное имя 'protected_api'


@protected_api_blueprint.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """Защищённый эндпоинт, доступный только с JWT-токеном."""
    response_data = {'message': 'This is a protected endpoint'}
    return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 200
