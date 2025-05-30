from app import create_app, db
from app.models import Notification, User
from datetime import datetime, timedelta

def test_notifications():
    app = create_app()
    with app.app_context():
        # Очищаем существующие уведомления
        Notification.query.delete()
        
        # Получаем тестового пользователя (предполагаем, что он уже существует)
        test_user = User.query.filter_by(email='students@mai.education').first()
        if not test_user:
            print("Тестовый пользователь не найден!")
            return
        
        # Создаем тестовые уведомления
        notifications = [
            Notification(
                user_id=test_user.user_id,
                type='cancelled',
                subject_name='Математический анализ',
                message='Пара "Математический анализ" за 20.05 18:00 была отменена',
                created_at=datetime.utcnow() - timedelta(hours=2)
            ),
            Notification(
                user_id=test_user.user_id,
                type='cancelled',
                subject_name='Физика',
                message='Пара "Физика" за 21.05 10:30 была отменена',
                created_at=datetime.utcnow() - timedelta(hours=1)
            ),
            Notification(
                user_id=test_user.user_id,
                type='changed',
                subject_name='Программирование',
                message='Пара "Программирование" перенесена с 22.05 14:00 на 22.05 16:00',
                created_at=datetime.utcnow() - timedelta(minutes=30)
            )
        ]
        
        # Добавляем уведомления в базу данных
        for notification in notifications:
            db.session.add(notification)
        
        # Сохраняем изменения
        db.session.commit()
        print("Тестовые уведомления успешно добавлены!")
        
        # Проверяем, что уведомления действительно добавлены
        saved_notifications = Notification.query.filter_by(user_id=test_user.user_id).all()
        print(f"\nДобавлено уведомлений: {len(saved_notifications)}")
        for notification in saved_notifications:
            print(f"\nУведомление #{notification.notification_id}:")
            print(f"Тип: {notification.type}")
            print(f"Предмет: {notification.subject_name}")
            print(f"Сообщение: {notification.message}")
            print(f"Создано: {notification.created_at}")
            print(f"Прочитано: {notification.is_read}")

if __name__ == '__main__':
    test_notifications() 