import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Проверка наличия ключей
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for Flask application. Please set it in backend/.env.")
    if not JWT_SECRET_KEY:
        raise ValueError("No JWT_SECRET_KEY set for JWT. Please set it in backend/.env.")
