import json
from collections import defaultdict
from datetime import datetime, timedelta
from flask import Blueprint, Response, request, jsonify
from ..models import Group, Schedule, Week
from ..scraper.downloader import ScheduleDownloader
from .. import db
from ..utils import shorten_teacher_name

schedule_api_blueprint = Blueprint('schedule_api', __name__, url_prefix='/api')

def format_date_russian(date_str):
    """Форматирование даты для отображения."""
    day, month, year = date_str.split('.')
    months = {
        '01': 'января', '02': 'февраля', '03': 'марта',
        '04': 'апреля', '05': 'мая', '06': 'июня',
        '07': 'июля', '08': 'августа', '09': 'сентября',
        '10': 'октября', '11': 'ноября', '12': 'декабря'
    }
    return f"{int(day)} {months[month]}"

@schedule_api_blueprint.route('/schedule_groups', methods=['POST'])
def schedule_groups():
    """Получение списка групп для выбранного института, курса и уровня обучения."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Отсутствуют данные в запросе'}), 400

        print("Получен запрос:", data)

        institute_name = data.get('institute_name')
        course_number = data.get('course_number')
        level_name = data.get('level_name')

        if not all([institute_name, course_number, level_name]):
            return jsonify({'error': 'Отсутствуют обязательные параметры'}), 400

        print(f"Параметры: институт={institute_name}, курс={course_number}, уровень={level_name}")

        # Извлекаем номер института из названия
        try:
            if "№" in institute_name:
                institute_number = institute_name.split('№')[-1].strip()
            elif "Передовая инженерная школа" in institute_name:
                institute_number = "14"
            else:
                # Пробуем найти число в названии
                import re
                numbers = re.findall(r'\d+', institute_name)
                if numbers:
                    institute_number = numbers[0]
                else:
                    raise ValueError(f"Не удалось определить номер института из названия: {institute_name}")
            
            print(f"Определен номер института: {institute_number}")
        except Exception as e:
            print(f"Ошибка при определении номера института: {e}")
            return jsonify({'error': f'Ошибка при определении номера института: {str(e)}'}), 400

        # Получаем актуальный список групп с сайта МАИ
        try:
            print(f"Запрашиваем группы для института {institute_number}, курс {course_number}, уровень {level_name}")
            groups = ScheduleDownloader.get_all_groups(
                institute_number=institute_number,
                course=course_number,
                education_level=level_name
            )
            print("Найдены группы:", groups)

            if not groups:
                return jsonify({'error': 'Группы не найдены'}), 404

            return jsonify({'groups': groups})

        except Exception as e:
            print(f"Ошибка при получении групп: {e}")
            return jsonify({'error': f'Ошибка при получении групп: {str(e)}'}), 500

    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500


@schedule_api_blueprint.route('/schedule_week', methods=['POST'])
def schedule_all():
    """Неавторизированное расписание. Вывод всего расписания на неделю"""
    data = request.get_json()
    group_code = data.get('group_code')
    date = data.get('date')

    print(f"\nЗапрос расписания:")
    print(f"Группа: {group_code}")
    print(f"Дата: {date}")

    try:
        current_date = datetime.strptime(date, "%d.%m.%Y")
    except ValueError:
        response_data = {'error': 'Invalid date format, expected DD.MM.YYYY'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 400

    weeks = Week.query.all()
    week = None
    for i in weeks:
        start_date = datetime.strptime(i.week_start, "%d.%m.%Y")
        end_date = datetime.strptime(i.week_end, "%d.%m.%Y")
        if start_date <= current_date <= end_date:
            week = i
            break

    if not week:
        print("Неделя не найдена")
        response_data = {'error': 'Invalid date'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 404

    week_num = week.week_num
    print(f"Найдена неделя: {week_num} ({week.week_start} - {week.week_end})")

    schedules = Schedule.query.filter_by(
        week_num=week_num,
        group_code=group_code
    ).all()

    print(f"Найдено занятий: {len(schedules)}")

    # Вычисляем даты для каждого дня недели
    day_dates = {}
    week_start = datetime.strptime(week.week_start, "%d.%m.%Y")
    days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    for i, day in enumerate(days_of_week):
        day_date = week_start + timedelta(days=i)
        day_dates[day] = format_date_russian(day_date.strftime("%d.%m.%Y"))

    # Собираем json с расписанием на неделю
    schedule_by_day = defaultdict(list)
    for schedule in schedules:
        schedule_by_day[schedule.day].append(schedule)

    result = []
    for day in days_of_week:
        day_schedules = schedule_by_day.get(day, [])
        lessons = []
        for schedule in day_schedules:
            lesson = {
                'subject': schedule.subject_code,
                'type': schedule.subject_type,
                'time': schedule.time_slot,
                'teacher': shorten_teacher_name(schedule.teacher.full_name) if schedule.teacher else "",
                'room': schedule.room_number
            }
            lessons.append(lesson)
        day_obj = {
            'day': f"{day}, {day_dates[day]}",
            'lessons': lessons
        }
        result.append(day_obj)

    print("Отправляем ответ:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    response_data = json.dumps(result, ensure_ascii=False)
    return Response(response_data, mimetype='application/json'), 200


@schedule_api_blueprint.route('/schedule/change-week', methods=['POST'])
def change_week():
    data = request.get_json()
    group_code = data.get('group_code')
    date = data.get('date')
    direction = data.get('direction')

    try:
        current_date = datetime.strptime(date, "%d.%m.%Y")
    except ValueError:
        response_data = {'error': 'Invalid date format, expected DD.MM.YYYY'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 400

    if direction == 'prev':
        target_date = current_date - timedelta(days=7)
    elif direction == 'next':
        target_date = current_date + timedelta(days=7)
    else:
        response_data = {'error': 'Invalid direction, expected "prev" or "next"'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 400

    weeks = Week.query.all()
    week = None
    for i in weeks:
        start_date = datetime.strptime(i.week_start, "%d.%m.%Y")
        end_date = datetime.strptime(i.week_end, "%d.%m.%Y")
        if start_date <= target_date <= end_date:
            week = i
            break

    if not week:
        response_data = {'error': 'No schedule found for the target week'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 404

    week_num = week.week_num

    schedules = Schedule.query.filter_by(
        week_num=week_num,
        group_code=group_code
    ).all()

    if not schedules:
        response_data = {'error': 'No schedule found for the group and week'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 404

    schedule_by_day = defaultdict(list)
    for schedule in schedules:
        schedule_by_day[schedule.day].append(schedule)

    result = []
    for day, schedules in schedule_by_day.items():
        lessons = []
        for schedule in schedules:
            lesson = {
                'subject': schedule.subject_code,
                'type': schedule.subject_type,
                'time': schedule.time_slot,
                'teacher': shorten_teacher_name(schedule.teacher.full_name),
                'room': schedule.room_number
            }
            lessons.append(lesson)
        day_obj = {
            'day': day,
            'lessons': lessons
        }
        result.append(day_obj)

    response_data = json.dumps(result, ensure_ascii=False)
    return Response(response_data, mimetype='application/json'), 200
