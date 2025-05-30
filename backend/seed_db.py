from app import db, create_app
from app.models import Institute, Level, Group, Week, Subject, Teacher, Course, User, StudentProfile
from app.scraper.downloader import ScheduleDownloader
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def create_weeks():
    """Создание трех недель (предыдущая, текущая, следующая)."""
    # Находим ближайший понедельник
    today = datetime.now()
    days_until_monday = (today.weekday() - 0) % 7
    nearest_monday = today - timedelta(days=days_until_monday)
    
    # Начало учебного года (первый понедельник февраля)
    start_date = datetime(2025, 2, 10)  # 10.02.2025 - начало первой недели
    
    # Вычисляем номер текущей недели
    days_diff = (nearest_monday - start_date).days
    current_week_num = (days_diff // 7) + 1  # +1 потому что первая неделя имеет номер 1
    
    print(f"Текущая неделя: {current_week_num}")
    
    # Создаем три недели
    weeks = []
    for i in range(-1, 2):
        week_start = nearest_monday + timedelta(days=i*7)
        week_end = week_start + timedelta(days=6)
        week_num = current_week_num + i
        week = Week(
            week_num=week_num,
            week_start=week_start.strftime('%d.%m.%Y'),
            week_end=week_end.strftime('%d.%m.%Y')
        )
        weeks.append(week)
    
    # Сохраняем в базу данных
    db.session.add_all(weeks)
    db.session.commit()
    
    print("Создано 3 недель:")
    for week in weeks:
        print(f"Неделя {week.week_num}: {week.week_start} - {week.week_end}")
    
    return weeks

def load_schedule_for_week(app, group, week_num):
    """Загрузка расписания для конкретной недели."""
    with app.app_context():
        print(f"  Неделя {week_num}")
        downloader = ScheduleDownloader(group.group_code, week_num)
        html = downloader.get_html(force_reload=True)
        if html:
            print("  HTML получен, начинаем парсинг...")
            result = downloader.parse_schedule_html(html)
            if result:
                print(f"  Расписание для недели {week_num} успешно загружено")
            else:
                print(f"  Ошибка при загрузке расписания для недели {week_num}")
            return result
        else:
            print(f"  Не удалось получить HTML для недели {week_num}")
            return False

def seed_database():
    """Заполнение базы данных тестовыми данными."""
    app = create_app()
    
    with app.app_context():
        # Очищаем базу данных
        db.drop_all()
        db.create_all()

        # Создаем тестового пользователя
        test_profile = StudentProfile(
            first_name='Тест',
            last_name='Пользователь',
            gender='male',
            language='ru',
            group_code='М8О-105БВ-24'
        )
        db.session.add(test_profile)
        db.session.flush()

        test_user = User(
            email='students@mai.education',
            profile_id=test_profile.profile_id
        )
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.flush()

        # Создаем институты
        institutes = [
            Institute(institute_code='М8', institute_name='Институт №8'),
            Institute(institute_code='М9', institute_name='Институт №9')
        ]
        db.session.add_all(institutes)
        db.session.flush()

        # Создаем уровни образования
        levels = [
            Level(level_code='БВ', level_name='Базовое высшее образование'),
            Level(level_code='СВ', level_name='Специализированное высшее образование'),
            Level(level_code='А', level_name='Аспирантура')
        ]
        db.session.add_all(levels)
        db.session.flush()

        # Создаем курсы
        courses = [
            Course(course_number='1'),
            Course(course_number='2'),
            Course(course_number='3'),
            Course(course_number='4')
        ]
        db.session.add_all(courses)
        db.session.flush()

        # Создаем группы
        groups = [
            Group(group_code='М8О-105БВ-24', course_number='1', institute_name=institutes[0].institute_name, level_name=levels[0].level_name)
        ]
        db.session.add_all(groups)
        db.session.flush()

        # Создаем недели
        weeks = create_weeks()

        # Загружаем расписание для всех недель последовательно
        print("\nЗагрузка расписания для группы М8О-105БВ-24...")
        results = []
        for week in weeks:
            result = load_schedule_for_week(app, groups[0], week.week_num)
            results.append(result)
            
        if all(results):
            print("\nРасписание успешно загружено для всех недель")
        else:
            print("\nВНИМАНИЕ: Не удалось загрузить расписание для некоторых недель")

        db.session.commit()
        print("\nБаза данных успешно заполнена тестовыми данными")
        print("Примечание: seed_db нужно запускать отдельно при первом запуске проекта для заполнения базы данных.")

if __name__ == '__main__':
    seed_database() 