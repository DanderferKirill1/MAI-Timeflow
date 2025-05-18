import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')  # создайте свой и поместите в /backend/.env
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"  # путь к бд
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Отключаем отслеживание модификаций для экономии ресурсов
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')  # то же, что и для SECRET_KEY


# Проверка наличия ключей
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for Flask application. Please set it in backend/.env.")
    if not JWT_SECRET_KEY:
        raise ValueError("No JWT_SECRET_KEY set for JWT. Please set it in backend/.env.")
