from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # объект для работы с бд
jwt = JWTManager()  # объект для управления JWT


def create_app():
    app = Flask(
        __name__,
        template_folder="../../frontend/templates",
        static_folder="../../frontend/static"
    )

    from instance.config import Config
    app.config.from_object(Config)  # Загрузка конфигурации из instance/config.py

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5500"}})
    db.init_app(app)
    jwt.init_app(app)

    from .routes import api_blueprint, frontend_blueprint

    app.register_blueprint(api_blueprint)
    app.register_blueprint(frontend_blueprint)

    # Создание таблиц в бд
    with app.app_context():
        db.create_all()

    return app
