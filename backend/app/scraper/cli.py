import click
from .downloader import ScheduleDownloader
from .parser import json_to_db_models, parse_schedule_html
from .. import create_app
from ..models import Group, Institute, Schedule, Teacher
import re


def parse_week_range(week_str):
    """Парсит строку диапазона недель (например, '1-10' или '35')."""
    if '-' in week_str:
        start, end = map(int, week_str.split('-'))
        return list(range(start, end + 1))
    else:
        return [int(week_str)]

@click.command()
@click.option('--group', required=True, help='Код группы (например, М8О-105БВ-24)')
@click.option('--week', required=True, help='Номер недели или диапазон (например, 15 или 1-52)')
@click.option('--force-reload', is_flag=True, help='Принудительно загрузить расписание, игнорируя кэш')
def scrape_schedule(group: str, week: str, force_reload: bool):
    """CLI-утилита для загрузки и сохранения расписания группы в БД."""

    app = create_app()
    with app.app_context():
        try:
            weeks = parse_week_range(week)
            for w in weeks:
                print(f"\nЗагрузка расписания для группы {group}, неделя {w}...")
                downloader = ScheduleDownloader(group, w)
                html = downloader.get_html(force_reload=force_reload)
                if not html:
                    print(f"Не удалось получить HTML расписания для недели {w}.")
                    continue
                json_data = parse_schedule_html(html)
                json_to_db_models(json_data, group, w)
                print(f"Расписание для группы {group} на неделю {w} успешно сохранено в БД.")

            schedules = Schedule.query.join(Teacher, Schedule.teacher_id == Teacher.teacher_id).filter(Schedule.group_code == group).all()
            for schedule in schedules:
                print(schedule, schedule.teacher.full_name)

            groups = Group.query.all()
            for group in groups:
                print(group)

            institutes = Institute.query.all()
            for institute in institutes:
                print(institute)

        except Exception as e:
            click.secho(f"Ошибка: {str(e)}", fg="red", err=True)


if __name__ == '__main__':
    scrape_schedule()
