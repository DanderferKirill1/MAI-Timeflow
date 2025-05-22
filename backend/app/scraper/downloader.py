import os
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


class ScheduleDownloader:
    """Класс для загрузки HTML расписания с сайта МАИ."""

    BASE_URL = "https://mai.ru/education/studies/schedule/groups.php?"
    CACHE_DIR = "backend/cache"
    EDUCATION_LEVEL_MAP = {
        'СВ': 'Специализированное высшее образование',
        'БВ': 'Базовое высшее образование',
        'А': 'Аспирантура',
        'М': 'Магистратура',
        'Б': 'Бакалавриат'
    }

    def __init__(self, group_code: str, week_number: int):
        self.group_code = group_code
        self.week_number = week_number
        self.driver = None
        os.makedirs(self.CACHE_DIR, exist_ok=True)

    def parse_group_code(self):
        """Извлечение информации из кода группы."""
        result = {'group_code': self.group_code}
        parsed = self.group_code.split('-')

        # Номер института
        if parsed[0][1] == 'И':
            result['institute_number'] = '10'
        else:
            inst_block = parsed[0][1:]  # Убираем первую букву
            institute_number = ''.join(filter(str.isdigit, inst_block))
            result['institute_number'] = institute_number

        # Курс
        group_section = parsed[1]
        digits = ''
        for char in group_section:
            if char.isdigit():
                digits += char
            else:
                rest = group_section[len(digits):]
                break
        result['course'] = digits[0]

        # Ступень образования
        level = None
        for key in self.EDUCATION_LEVEL_MAP:
            if rest.startswith(key):
                level = self.EDUCATION_LEVEL_MAP[key]
                break
        result['education_level'] = level

        return result

    def get_cache_path(self):
        """Путь к файлу кэша."""
        return os.path.join(self.CACHE_DIR, f"{self.group_code}_{self.week_number}.html")

    def load_from_cache(self):
        """Попытка загрузки HTML из кэша."""
        cache_path = self.get_cache_path()
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def save_to_cache(self, html):
        """Сохранение HTML в кэш."""
        cache_path = self.get_cache_path()
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def get_html(self, force_reload=False, max_attempts=3):
        """Получение HTML расписания."""
        # Проверка кэша
        if not force_reload:
            cached_html = self.load_from_cache()
            if cached_html:
                return cached_html

        self.driver = webdriver.Chrome()
        self.driver.get(self.BASE_URL)

        old_url = self.driver.current_url
        for attempt in range(1, max_attempts + 1):
            try:
                group_info = self.parse_group_code()
                institute = group_info['institute_number']
                course = group_info['course']
                edu_level = group_info['education_level']

                wait = WebDriverWait(self.driver, 10)

                # Выбор института
                institute_bt = wait.until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, "select#department"))
                )
                if institute == '14':
                    Select(institute_bt).select_by_value("Передовая инженерная школа")
                else:
                    Select(institute_bt).select_by_value(f"Институт №{institute}")

                # Выбор курса
                course_bt = wait.until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, "select#course"))
                )
                Select(course_bt).select_by_value(course)

                # Нажатие "Отобразить"
                submit_button = wait.until(
                    ec.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
                )
                self.driver.execute_script("arguments[0].click();", submit_button)

                # Выбор уровня обучения
                xpath = (
                    f"//a[@data-bs-toggle='pill'"
                    f" and contains(@data-bs-target, '-eg1')"
                    f" and normalize-space(text())='{edu_level}']"
                )
                edu_tab = wait.until(ec.element_to_be_clickable((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].click();", edu_tab)

                # Выбор группы
                group = wait.until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, f"a[href*='group={self.group_code}']"))
                )
                self.driver.execute_script("arguments[0].click();", group)

                # Проверка перехода
                try:
                    WebDriverWait(self.driver, 2).until(lambda d: d.current_url != old_url)
                except TimeoutException:
                    self.driver.get(self.BASE_URL)
                    raise TimeoutException("Переход к расписанию группы не произошёл.")

                # Переход на нужную неделю
                current_url = self.driver.current_url
                if "week=" in current_url:
                    current_url = current_url.split("&week=")[0]
                self.driver.get(f"{current_url}&week={self.week_number}")

                # Извлечение расписания
                try:
                    schedule_block = wait.until(ec.presence_of_element_located(
                        (By.CSS_SELECTOR, "ul.step.mb-5")
                    ))
                    html = schedule_block.get_attribute("innerHTML")
                    self.save_to_cache(html)
                    print(f"Успешно загружено с попытки {attempt}")
                    return html
                except TimeoutException:
                    raise TimeoutException("Блок с расписанием не найден.")

            except Exception as e:
                print(f"Попытка {attempt} не удалась: {e}")
                if attempt == max_attempts:
                    raise Exception(f"Не удалось загрузить расписание после {max_attempts} попыток.")
            finally:
                if attempt == max_attempts:
                    self.driver.quit()
