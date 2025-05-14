from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from . import db
from .models import Schedule, Subject, Teacher, Group


class ScheduleLoader:
    def __init__(self):
        """Инициализация загрузчика расписания с использованием Selenium."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.cache = {}

    def load_schedule(self, group_code, week_number):
        """
        Загружает расписание для указанной группы и недели.

        :param group_code: Код группы (например, 'М3О-101Б-21')
        :param week_number: Номер недели (например, '1')
        :return: HTML-код страницы с расписанием
        """
        cache_key = f"{group_code}_{week_number}"
        if cache_key in self.cache:
            print(f"Загружено из кэша: {cache_key}")
            return self.cache[cache_key]

        url = "https://mai.ru/education/studies/schedule/groups.php"
        self.driver.get(url)

        try:
            # Ожидание загрузки элемента для ввода группы
            group_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "group"))
            )
        except:
            try:
                group_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "group"))
                )
            except:
                group_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'group')]"))
                )

        group_input.clear()
        group_input.send_keys(group_code)

        # Ожидание элемента для ввода недели
        try:
            week_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "week"))
            )
        except:
            week_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "week"))
            )

        week_input.clear()
        week_input.send_keys(week_number)

        # Ожидание кнопки отправки формы
        submit_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
        )
        submit_button.click()

        # Ожидание загрузки расписания
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "schedule-table"))
        )

        html_content = self.driver.page_source
        self.cache[cache_key] = html_content
        return html_content

    def get_parsed_schedule(self, group_code, week_number):
        """
        Загружает и парсит расписание.

        :param group_code: Код группы
        :param week_number: Номер недели
        :return: Список занятий
        """
        html_content = self.load_schedule(group_code, week_number)
        parser = ScheduleParser(html_content)
        return parser.parse_schedule()

    def close(self):
        """Закрывает драйвер Selenium."""
        self.driver.quit()


class ScheduleParser:
    def __init__(self, html_content):
        """Инициализация парсера с HTML-кодом."""
        self.soup = BeautifulSoup(html_content, "html.parser")

    def parse_schedule(self):
        """
        Парсит расписание из HTML и возвращает список занятий.

        :return: Список словарей с данными о занятиях
        """
        schedule = []
        table = self.soup.find("table", {"class": "schedule-table"})
        if not table:
            return schedule

        rows = table.find_all("tr")[1:]  # Пропускаем заголовок
        current_day = None

        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 1:  # День недели
                current_day = cols[0].text.strip()
            elif len(cols) >= 5 and current_day:  # Занятие
                time_slot = cols[0].text.strip()
                subject_name = cols[1].text.strip()
                room_number = cols[2].text.strip()
                teacher_name = cols[3].text.strip()

                schedule.append({
                    "weekday": current_day,
                    "time_slot": time_slot,
                    "subject_name": subject_name,
                    "room_number": room_number,
                    "teacher_name": teacher_name
                })

        return schedule


def save_schedule_to_db(parsed_schedule, group_code):
    """
    Сохраняет распарсенное расписание в базу данных.

    :param parsed_schedule: Список занятий
    :param group_code: Код группы
    """
    # Проверка существования группы
    group = Group.query.get(group_code)
    if not group:
        group = Group(group_code=group_code, group_name=group_code, course_number="unknown")
        db.session.add(group)
        db.session.commit()

    for lesson in parsed_schedule:
        # Поиск или создание предмета
        subject = Subject.query.filter_by(subject_name=lesson["subject_name"]).first()
        if not subject:
            subject_code = lesson["subject_name"][:10]  # Упрощение, можно улучшить
            subject = Subject(subject_code=subject_code, subject_name=lesson["subject_name"])
            db.session.add(subject)
            db.session.commit()

        # Поиск или создание преподавателя
        teacher = Teacher.query.filter_by(full_name=lesson["teacher_name"]).first()
        if not teacher:
            teacher = Teacher(full_name=lesson["teacher_name"])
            db.session.add(teacher)
            db.session.commit()

        # Создание записи расписания
        schedule_entry = Schedule(
            group_code=group_code,
            weekday=lesson["weekday"],
            time_slot=lesson["time_slot"],
            subject_code=subject.subject_code,
            room_number=lesson["room_number"],
            teacher_id=teacher.teacher_id
        )
        db.session.add(schedule_entry)

    db.session.commit()
    print(f"Расписание для группы {group_code} успешно сохранено в БД!")