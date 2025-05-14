import os
from dotenv import load_dotenv

# Явно указываем путь к файлу .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for Flask application. Please set it in backend/.env.")
    if not JWT_SECRET_KEY:
        raise ValueError("No JWT_SECRET_KEY set for JWT. Please set it in backend/.env.")