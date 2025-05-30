import os
import sys

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import NotificationSettings, User

def upgrade():
    app = create_app()
    with app.app_context():
        # Создаем таблицу notification_settings
        db.create_all()
        
        # Получаем всех пользователей
        users = User.query.all()
        
        # Создаем настройки по умолчанию для каждого пользователя
        for user in users:
            settings = NotificationSettings(
                user_id=user.user_id,
                schedule_changes=True,
                lesson_reminders=True,
                reminder_time=15,
                push_notifications=True,
                email_notifications=True,
                telegram_notifications=False
            )
            db.session.add(settings)
        
        db.session.commit()
        print("Миграция успешно выполнена!")

def downgrade():
    app = create_app()
    with app.app_context():
        # Удаляем таблицу notification_settings
        db.drop_all()
        print("Откат миграции выполнен!")

if __name__ == '__main__':
    upgrade() 