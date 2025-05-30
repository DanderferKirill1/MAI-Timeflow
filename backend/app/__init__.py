from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from config import Config


db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(
        __name__,
        template_folder="../../frontend/templates",
        static_folder="../../public/static"
    )

    app.config['JSONIFY_ENSURE_ASCII'] = False

    app.config.from_object(Config)

    # Настройка CORS
    CORS(app, resources={r"/api/*": {
        "origins": [
            "http://localhost:5500",
            "http://127.0.0.1:5500",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }})

    # Настройка JWT
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # В продакшене использовать безопасный ключ
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)  # Увеличиваем время жизни токена до 24 часов
    jwt.init_app(app)

    # Инициализация базы данных
    db.init_app(app)

    # Импорт и регистрация blueprints
    from .routes.frontend_routes import frontend_blueprint
    from .routes.auth_routes import auth_api_blueprint
    from .routes.protected_routes import protected_api_blueprint
    from .routes.schedule_rotes import schedule_api_blueprint

    app.register_blueprint(frontend_blueprint)
    app.register_blueprint(auth_api_blueprint)
    app.register_blueprint(protected_api_blueprint)
    app.register_blueprint(schedule_api_blueprint)

    with app.app_context():
        db.create_all()

    return app