from bs4 import BeautifulSoup
from datetime import datetime

from .downloader import ScheduleDownloader
from .. import db
from ..models import Course, Group, Institute, Level, Schedule, Subject, Teacher, Week, Notification, User

DAY_MAP = {
    'Пн': 'Понедельник',
    'Вт': 'Вторник',
    'Ср': 'Среда',
    'Чт': 'Четверг',
    'Пт': 'Пятница',
    'Сб': 'Суббота',
    'Вс': 'Воскресенье',
}


def parse_schedule_html(html: str):
    """Парсинг HTML в JSON-формат."""
    soup = BeautifulSoup(html, "html.parser")
    result = []

    for li in soup.select("li.step-item"):
        raw_title = li.select_one(".step-title").get_text(strip=True).replace("\xa0", " ")
        weekday_short, date = map(str.strip, raw_title.split(",", 1))
        weekday = DAY_MAP.get(weekday_short, weekday_short)

        day_obj = {"day": weekday + ' ' + date, "lessons": []}

        for lesson in li.select("div.mb-4"):
            title_tag = lesson.select_one("p.fw-semi-bold")
            badge = title_tag.select_one("span.badge")
            type_code = badge.get_text(strip=True) if badge else ""

            subject_text = title_tag.get_text(" ", strip=True)[:-3]

            time_tag = lesson.select_one("ul.list-inline li.list-inline-item")
            time_txt = time_tag.get_text(strip=True) if time_tag else ""

            atags = lesson.select("ul.list-inline li.list-inline-item a[href*='ppc.php']")
            teacher = atags[0].get_text(strip=True) if atags else ""

            room_tag = lesson.select_one("ul.list-inline li.list-inline-item i.fa-map-marker-alt")
            room = room_tag.find_parent("li").get_text(strip=True) if room_tag else ""

            day_obj["lessons"].append({
                "subject": subject_text,
                "type": type_code,
                "time": time_txt,
                "teacher": teacher,
                "room": room,
            })

        result.append(day_obj)

    return result


def compare_schedules(old_schedule, new_schedule, group_code):
    """Сравнение старого и нового расписания, отправка уведомлений об изменениях."""
    try:
        # Получаем всех пользователей с этой группой
        users = User.query.filter_by(group_code=group_code).all()
        if not users:
            print(f"Пользователи с группой {group_code} не найдены")
            return

        # Создаем словари для быстрого поиска
        old_schedule_dict = {(s.day, s.time_slot, s.subject_code): s for s in old_schedule}
        new_schedule_dict = {(s.day, s.time_slot, s.subject_code): s for s in new_schedule}

        # Находим отмененные пары
        for key, old_lesson in old_schedule_dict.items():
            if key not in new_schedule_dict:
                # Пара отменена
                for user in users:
                    notification = Notification(
                        user_id=user.user_id,
                        type='cancelled',
                        subject_name=old_lesson.subject_code,
                        message=f'Пара "{old_lesson.subject_code}" за {old_lesson.day} {old_lesson.time_slot} была отменена',
                        created_at=datetime.utcnow(),
                        is_read=False
                    )
                    db.session.add(notification)

        # Находим перенесенные пары
        for key, new_lesson in new_schedule_dict.items():
            if key not in old_schedule_dict:
                # Проверяем, не является ли это новой парой
                is_moved = False
                for old_key, old_lesson in old_schedule_dict.items():
                    if (old_lesson.subject_code == new_lesson.subject_code and 
                        old_lesson.time_slot != new_lesson.time_slot):
                        # Пара перенесена
                        is_moved = True
                        for user in users:
                            notification = Notification(
                                user_id=user.user_id,
                                type='changed',
                                subject_name=new_lesson.subject_code,
                                message=f'Пара "{new_lesson.subject_code}" перенесена с {old_lesson.day} {old_lesson.time_slot} на {new_lesson.day} {new_lesson.time_slot}',
                                created_at=datetime.utcnow(),
                                is_read=False
                            )
                            db.session.add(notification)
                        break

        db.session.commit()
        print("Уведомления об изменениях в расписании отправлены")
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при сравнении расписаний: {str(e)}")


def json_to_db_models(json_data, group_code, week_num):
    """Преобразование JSON в модели SQLAlchemy и сохранение в БД."""
    try:
        # Проверяем неделю
        week = Week.query.filter_by(week_num=week_num).first()
        if not week:
            raise ValueError(f"Запись для недели {week_num} не найдена в бд")

        # Парсим group_code для получения course_number и institute_number
        downloader = ScheduleDownloader(group_code, 0)  # week_number не нужен
        group_info = downloader.parse_group_code()  # так как нужен только этот метод
        course_number = group_info['course']
        institute_number = group_info['institute_number']
        level_name = group_info['education_level']

        for key in downloader.EDUCATION_LEVEL_MAP:
            if downloader.EDUCATION_LEVEL_MAP[key] == level_name:
                level_code = key

        # Проверяем/создаём институт
        institute_code = f"И-{institute_number}"
        institute_name = f"Институт №{institute_number}"
        institute = Institute.query.filter_by(institute_code=institute_code).first()
        if not institute:
            institute = Institute(institute_code=institute_code, institute_name=institute_name)
            db.session.add(institute)
            db.session.flush()

        # Проверяем/создаём курс
        course = Course.query.filter_by(course_number=course_number).first()
        if not course:
            course = Course(course_number=course_number)
            db.session.add(course)
            db.session.flush()

        # Проверяем/создаём уровень обучения
        level = Level.query.filter_by(level_code=level_code).first()
        if not level:
            level = Level(level_code=level_code, level_name=level_name)
            db.session.add(level)
            db.session.flush()

        # Проверяем/создаём группу
        group = Group.query.filter_by(group_code=group_code).first()
        if not group:
            group = Group(
                group_code=group_code,
                course_number=course_number,
                institute_name=institute_name,
                level_name=level_name)
            db.session.add(group)
            db.session.flush()

        # Получаем старое расписание
        old_schedule = Schedule.query.filter_by(
            group_code=group_code,
            week_num=week_num
        ).all()

        # Удаляем прошлые записи группы на заданную неделю
        Schedule.query.filter(Schedule.group_code == group_code, Schedule.week_num == week_num).delete()
        db.session.commit()

        # Загружаем данные
        new_schedule = []
        for day_data in json_data:
            day = day_data['day']
            for lesson in day_data['lessons']:
                # Проверяем/создаём предмет
                subject_name = lesson['subject']
                subject = Subject.query.filter_by(subject_code=subject_name).first()
                if not subject:
                    subject = Subject(subject_code=subject_name)
                    db.session.add(subject)
                    db.session.flush()

                # Проверяем/создаём преподавателя
                teacher_name = lesson['teacher']
                teacher = Teacher.query.filter_by(full_name=teacher_name).first()
                if not teacher:
                    teacher = Teacher(full_name=teacher_name)
                    db.session.add(teacher)
                    db.session.flush()

                # Создаём запись расписания
                schedule = Schedule(
                    week_num=week_num,
                    group_code=group_code,
                    day=day,
                    time_slot=lesson['time'],
                    subject_code=subject_name,
                    subject_type=lesson['type'],
                    room_number=lesson['room'],
                    teacher_id=teacher.teacher_id,
                )
                db.session.add(schedule)
                new_schedule.append(schedule)

        db.session.commit()

        # Сравниваем расписания и отправляем уведомления
        compare_schedules(old_schedule, new_schedule, group_code)

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Ошибка сохранения в БД: {str(e)}")
