import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
    # Базовый путь к директории проекта
    BASE_DIR = Path(__file__).resolve().parent

    # Настройки базы данных
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Настройки безопасности
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-for-development')

    # Настройки CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ] 