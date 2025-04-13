# backend/app/__init__.py
from flask import Flask

from flask_cors import CORS

from .routes import api_blueprint  # Добавьте этот импорт


def create_app():
    app = Flask(__name__)

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5500"}})

    # Регистрируем blueprint
    app.register_blueprint(api_blueprint, url_prefix='/')

    return app
