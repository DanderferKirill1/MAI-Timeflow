from flask import Flask

from flask_cors import CORS

from .routes import api_blueprint


def create_app():
    app = Flask(__name__)

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5500"}})

    app.register_blueprint(api_blueprint, url_prefix='/')

    return app
