import os
from pathlib import Path

class Config:
    # Базовый путь к директории проекта
    BASE_DIR = Path(__file__).resolve().parent

    # Настройки базы данных
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Настройки безопасности
    SECRET_KEY = 'your-secret-key-here'  # В продакшене использовать безопасный ключ

    # Настройки CORS
    CORS_ORIGINS = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ] 