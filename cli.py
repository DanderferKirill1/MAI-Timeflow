import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

import argparse
from app.schedule_loader import ScheduleLoader, save_schedule_to_db
from app import create_app

def main():
    parser = argparse.ArgumentParser(description="Загрузка расписания МАИ")
    parser.add_argument("--group", required=True, help="Код группы")
    parser.add_argument("--week", required=True, help="Номер недели")
    args = parser.parse_args()

    app = create_app()  # Инициализация приложения для контекста БД
    with app.app_context():
        loader = ScheduleLoader()
        try:
            parsed_schedule = loader.get_parsed_schedule(args.group, args.week)
            save_schedule_to_db(parsed_schedule, args.group)
        finally:
            loader.close()

if __name__ == "__main__":
    main()

print(sys.path)