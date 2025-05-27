import click
from .downloader import ScheduleDownloader
from .parser import json_to_db_models, parse_schedule_html
from .. import create_app
from ..models import Group, Institute, Schedule, Teacher


@click.command()
@click.option('--group', required=True, help='Код группы (например, М8О-105БВ-24)')
@click.option('--week', required=True, type=int, help='Номер недели (например, 15)')
@click.option('--force-reload', is_flag=True, help='Принудительно загрузить расписание, игнорируя кэш')
def scrape_schedule(group: str, week: int, force_reload: bool):
    """CLI-утилита для загрузки и сохранения расписания группы в БД."""

    app = create_app()
    with app.app_context():
        try:
            # Инициализация загрузчика
            downloader = ScheduleDownloader(group, week)

            # Получение HTML
            html = downloader.get_html(force_reload=force_reload)
            if not html:
                raise Exception("Не удалось получить HTML расписания.")

            # Парсинг HTML в JSON
            json_data = parse_schedule_html(html)

            # Сохранение в БД
            json_to_db_models(json_data, group, week)

            click.echo(f"\nРасписание для группы {group} на неделю {week} успешно сохранено в БД.\n")

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
