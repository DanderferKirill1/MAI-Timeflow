import json
from collections import defaultdict
from datetime import datetime, timedelta
from flask import Blueprint, Response, request
from ..models import Group, Schedule, Week

schedule_api_blueprint = Blueprint('schedule_api', __name__, url_prefix='/api')


@schedule_api_blueprint.route('/schedule_groups', methods=['POST'])
def schedule_groups():
    """Неавторизированное расписание. Вывод групп по фильтру"""
    data = request.get_json()
    institute_name = data.get('institute_name')
    course_number = data.get('course')
    level_name = data.get('level')

    groups = Group.query.filter_by(
        institute_name=institute_name,
        course_number=course_number,
        level_name=level_name
    ).all()

    if not groups:
        response_data = {'error': 'No groups found'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 404

    response_data = {'groups': [group.group_code for group in groups]}
    return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 200


@schedule_api_blueprint.route('/schedule_week', methods=['POST'])
def schedule_all():
    """Неавторизированное расписание. Вывод всего расписания на неделю"""
    data = request.get_json()
    group_code = data.get('group_code')
    date = data.get('date')

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
        response_data = {'error': 'Invalid date'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 404

    week_num = week.week_num

    schedules = Schedule.query.filter_by(
        week_num=week_num,
        group_code=group_code
    ).all()

    if not schedules:
        response_data = {'error': 'No schedule found for the group and week'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 404

    # Собираем json с расписанием на неделю
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
                'teacher': schedule.teacher.full_name,
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


@schedule_api_blueprint.route('/schedule/change-week', methods=['POST'])
def change_week():
    data = request.get_json()
    date = data.get('date')
    group_code = data.get('group_code')
    direction = data.get('direction')  # "next" or "prev"

    try:
        date_obj = datetime.strptime(date, "%d.%m.%Y")
    except ValueError:
        response_data = {'error': 'Invalid date format, expected DD.MM.YYYY'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 400

    # Вычисляем дату для следующей или предыдущей недели
    if direction == 'next':
        date_obj += timedelta(days=7)
    elif direction == 'prev':
        date_obj -= timedelta(days=7)
    else:
        response_data = {'error': 'Invalid direction, use "next" or "prev"'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 400

    weeks = Week.query.all()
    week = None
    for i in weeks:
        start_date = datetime.strptime(i.week_start, "%d.%m.%Y")
        end_date = datetime.strptime(i.week_end, "%d.%m.%Y")
        if start_date <= date_obj <= end_date:
            week = i
            break

    if not week:
        response_data = {'error': 'Invalid date'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 404

    week_num = week.week_num

    schedules = Schedule.query.filter_by(
        week_num=week_num,
        group_code=group_code
    ).all()

    if not schedules:
        response_data = {'error': 'No schedule found for the group and week'}
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json'), 404

    # Собираем json с расписанием на неделю
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
                'teacher': schedule.teacher.full_name,
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
