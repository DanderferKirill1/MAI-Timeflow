from bs4 import BeautifulSoup

from .downloader import ScheduleDownloader
from .. import db
from ..models import Course, Group, Institute, Schedule, Subject, Teacher

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


def json_to_db_models(json_data, group_code):
    """Преобразование JSON в модели SQLAlchemy и сохранение в БД."""
    try:
        # Парсим group_code для получения course_number и institute_number
        downloader = ScheduleDownloader(group_code, 0)  # week_number не нужен
        group_info = downloader.parse_group_code()  # так как нужен только этот метод
        course_number = group_info['course']
        institute_number = group_info['institute_number']

        # Проверяем/создаём институт
        institute_code = f"И-{institute_number}"
        institute = Institute.query.filter_by(institute_code=institute_code).first()
        if not institute:
            institute = Institute(institute_code=institute_code, institute_name=f"Институт №{institute_number}")
            db.session.add(institute)
            db.session.flush()

        # Проверяем/создаём курс
        course = Course.query.filter_by(course_number=course_number).first()
        if not course:
            course = Course(course_number=course_number, institute_code=institute_code)
            db.session.add(course)
            db.session.flush()

        # Проверяем/создаём группу
        group = Group.query.filter_by(group_code=group_code).first()
        if not group:
            group = Group(group_code=group_code, course_number=course_number)
            db.session.add(group)
            db.session.flush()

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
                    group_code=group_code,
                    day=day,
                    time_slot=lesson['time'],
                    subject_code=subject_name,
                    subject_type=lesson['type'],
                    room_number=lesson['room'],
                    teacher_id=teacher.teacher_id
                )
                db.session.add(schedule)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Ошибка сохранения в БД: {str(e)}")
