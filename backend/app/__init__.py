from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(
        __name__,
        template_folder="../../frontend/templates",
        static_folder="../../public/static"
    )

    app.config['JSONIFY_ENSURE_ASCII'] = False

    from instance.config import Config  # Импорт относительно sys.path
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5500", "http://127.0.0.1:5500"]}})

    db.init_app(app)
    jwt.init_app(app)

    # Импорт и регистрация blueprints
    from .routes.frontend_routes import frontend_blueprint
    from .routes.auth_routes import auth_api_blueprint  # Обновлено имя
    from .routes.protected_routes import protected_api_blueprint  # Обновлено имя

    app.register_blueprint(frontend_blueprint)
    app.register_blueprint(auth_api_blueprint)
    app.register_blueprint(protected_api_blueprint)

    with app.app_context():
        db.create_all()

    return app
