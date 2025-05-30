import os
import json
from datetime import datetime, timedelta
from urllib.parse import unquote
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from app.models import Schedule, db, Subject


class ScheduleDownloader:
    """Класс для загрузки HTML расписания с сайта МАИ."""

    BASE_URL = "https://mai.ru/education/studies/schedule/groups.php?"
    CACHE_DIR = "cache"
    GROUPS_CACHE_FILE = "groups_cache.json"
    CACHE_LIFETIME = timedelta(hours=12)  # Кэш действителен 12 часов
    EDUCATION_LEVEL_MAP = {
        'СВ': 'Специализированное высшее образование',
        'БВ': 'Базовое высшее образование',
        'А': 'Аспирантура',
        'М': 'Магистратура',
        'Б': 'Бакалавриат'
    }

    def __init__(self, group_code: str = None, week_number: int = None):
        self.group_code = group_code
        self.week_number = week_number
        self.cache_dir = Path('cache')
        self.cache_dir.mkdir(exist_ok=True)
        
        # Оптимизированные настройки Chrome
        chrome_options = Options()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--silent')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        
        # Добавляем больше заголовков
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        chrome_options.add_argument('accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8')
        chrome_options.add_argument('accept-language=ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7')
        chrome_options.add_argument('sec-ch-ua="Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"')
        chrome_options.add_argument('sec-ch-ua-mobile=?0')
        chrome_options.add_argument('sec-ch-ua-platform="Windows"')
        chrome_options.add_argument('sec-fetch-dest=document')
        chrome_options.add_argument('sec-fetch-mode=navigate')
        chrome_options.add_argument('sec-fetch-site=none')
        chrome_options.add_argument('sec-fetch-user=?1')
        chrome_options.add_argument('upgrade-insecure-requests=1')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.actions = ActionChains(self.driver)

    @classmethod
    def _get_chrome_options(cls):
        """Настройки Chrome для оптимизации производительности."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Запуск в фоновом режиме
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-images')  # Отключаем загрузку изображений
        chrome_options.add_argument('--disable-javascript')  # Отключаем JavaScript где возможно
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        return chrome_options

    @classmethod
    def _load_groups_from_cache(cls, institute_number: str, course: str, education_level: str):
        """Загрузка списка групп из кэша."""
        cache_path = os.path.join(cls.CACHE_DIR, cls.GROUPS_CACHE_FILE)
        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # Проверяем актуальность кэша
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_time > cls.CACHE_LIFETIME:
                return None

            # Ищем нужные группы в кэше
            cache_key = f"{institute_number}_{course}_{education_level}"
            return cache_data['groups'].get(cache_key)
        except Exception as e:
            print(f"Ошибка при чтении кэша: {e}")
            return None

    @classmethod
    def _save_groups_to_cache(cls, institute_number: str, course: str, education_level: str, groups: list):
        """Сохранение списка групп в кэш."""
        cache_path = os.path.join(cls.CACHE_DIR, cls.GROUPS_CACHE_FILE)
        try:
            # Загружаем существующий кэш или создаем новый
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
            else:
                cache_data = {'groups': {}, 'timestamp': datetime.now().isoformat()}

            # Обновляем данные в кэше
            cache_key = f"{institute_number}_{course}_{education_level}"
            cache_data['groups'][cache_key] = groups
            cache_data['timestamp'] = datetime.now().isoformat()

            # Сохраняем кэш
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении кэша: {e}")

    @staticmethod
    def get_all_groups(institute_number: str, course: str, education_level: str):
        """Получение списка всех групп для заданного института, курса и уровня обучения."""
        # Пробуем загрузить из кэша
        cached_groups = ScheduleDownloader._load_groups_from_cache(institute_number, course, education_level)
        if cached_groups:
            print("Загружено из кэша")
            return cached_groups

        # Если в кэше нет, загружаем с сайта
        chrome_options = ScheduleDownloader._get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)
        groups = []
        
        try:
            driver.get(ScheduleDownloader.BASE_URL)
            wait = WebDriverWait(driver, 10)

            # Выбор института
            institute_bt = wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "select#department"))
            )
            if institute_number == '14':
                Select(institute_bt).select_by_value("Передовая инженерная школа")
            else:
                Select(institute_bt).select_by_value(f"Институт №{institute_number}")

            # Выбор курса
            course_bt = wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "select#course"))
            )
            Select(course_bt).select_by_value(course)

            # Нажатие "Отобразить"
            submit_button = wait.until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            driver.execute_script("arguments[0].click();", submit_button)

            # Выбор уровня обучения
            xpath = (
                f"//a[@data-bs-toggle='pill'"
                f" and contains(@data-bs-target, '-eg1')"
                f" and normalize-space(text())='{education_level}']"
            )
            edu_tab = wait.until(ec.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].click();", edu_tab)

            # Ждем, пока загрузится контент для выбранного уровня обучения
            content_id = edu_tab.get_attribute('data-bs-target').replace('#', '')
            wait.until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, f"#{content_id}"))
            )

            # Получение списка групп только из активного таба
            active_tab = wait.until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, f"#{content_id}"))
            )
            group_links = active_tab.find_elements(By.CSS_SELECTOR, "a[href*='group=']")
            
            for link in group_links:
                group_code = link.get_attribute('href').split('group=')[1].split('&')[0]
                # Декодируем URL-encoded строку
                decoded_group = unquote(group_code)
                groups.append(decoded_group)

            # Сохраняем результат в кэш
            ScheduleDownloader._save_groups_to_cache(institute_number, course, education_level, groups)

        except Exception as e:
            print(f"Ошибка при получении списка групп: {e}")
        finally:
            driver.quit()

        return groups

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

    def random_delay(self, min_seconds=0.5, max_seconds=1.0):
        """Случайная задержка между действиями для имитации человеческого поведения."""
        delay = random.uniform(min_seconds, max_seconds)
        print(f"Пауза {delay:.1f} секунд...")
        time.sleep(delay)

    def get_week_number_from_dates(self, start_date, end_date):
        """Определение номера учебной недели на основе дат."""
        # Преобразуем строки дат в объекты datetime
        start = datetime.strptime(start_date, '%d.%m.%Y')
        end = datetime.strptime(end_date, '%d.%m.%Y')
        
        # Определяем дату начала первой недели
        first_week_start = datetime.strptime('10.02.2025', '%d.%m.%Y')
        
        # Вычисляем разницу в неделях
        delta = start - first_week_start
        week_number = (delta.days // 7) + 1  # +1, так как первая неделя имеет номер 1
        
        return week_number

    def get_html(self, force_reload=False, max_attempts=3):
        """Получение HTML расписания."""
        if not force_reload:
            cached_html = self.load_from_cache()
            if cached_html:
                print("Загружено из кэша")
                return cached_html

        print(f"\nНачинаем загрузку расписания для группы {self.group_code}, неделя {self.week_number}")
        self.driver.get(self.BASE_URL)
        self.random_delay(0.5, 1.0)  # Уменьшенная начальная задержка

        old_url = self.driver.current_url
        for attempt in range(1, max_attempts + 1):
            try:
                print(f"\nПопытка {attempt} из {max_attempts}")
                group_info = self.parse_group_code()
                institute = group_info['institute_number']
                course = group_info['course']
                edu_level = group_info['education_level']

                wait = WebDriverWait(self.driver, 15)  # Увеличиваем время ожидания

                # Выбор института
                print("Выбираем институт...")
                institute_bt = wait.until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, "select#department"))
                )
                self.actions.move_to_element(institute_bt).perform()
                self.random_delay(0.3, 0.5)
                
                if institute == '14':
                    Select(institute_bt).select_by_value("Передовая инженерная школа")
                else:
                    Select(institute_bt).select_by_value(f"Институт №{institute}")
                self.random_delay(0.3, 0.5)

                # Выбор курса
                print("Выбираем курс...")
                course_bt = wait.until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, "select#course"))
                )
                self.actions.move_to_element(course_bt).perform()
                self.random_delay(0.3, 0.5)
                Select(course_bt).select_by_value(course)
                self.random_delay(0.3, 0.5)

                # Нажатие "Отобразить"
                print("Нажимаем кнопку 'Отобразить'...")
                submit_button = wait.until(
                    ec.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
                )
                self.actions.move_to_element(submit_button).perform()
                self.random_delay(0.3, 0.5)
                self.driver.execute_script("arguments[0].click();", submit_button)
                self.random_delay(0.5, 1.0)  # Уменьшенная задержка после отправки формы

                # Выбор уровня обучения
                print("Выбираем уровень обучения...")
                xpath = (
                    f"//a[@data-bs-toggle='pill'"
                    f" and contains(@data-bs-target, '-eg1')"
                    f" and normalize-space(text())='{edu_level}']"
                )
                edu_tab = wait.until(ec.element_to_be_clickable((By.XPATH, xpath)))
                self.actions.move_to_element(edu_tab).perform()
                self.random_delay(0.3, 0.5)
                self.driver.execute_script("arguments[0].click();", edu_tab)
                self.random_delay(0.3, 0.5)

                # Выбор группы
                print("Выбираем группу...")
                group = wait.until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, f"a[href*='group={self.group_code}']"))
                )
                self.actions.move_to_element(group).perform()
                self.random_delay(0.3, 0.5)
                self.driver.execute_script("arguments[0].click();", group)
                self.random_delay(0.5, 1.0)  # Уменьшенная задержка после выбора группы

                # Проверка перехода
                try:
                    WebDriverWait(self.driver, 5).until(lambda d: d.current_url != old_url)
                except TimeoutException:
                    print("Ошибка: переход к расписанию группы не произошёл")
                    self.driver.get(self.BASE_URL)
                    raise TimeoutException("Переход к расписанию группы не произошёл.")

                # Переход на нужную неделю
                print(f"Переходим на неделю {self.week_number}...")
                current_url = self.driver.current_url
                if "week=" in current_url:
                    current_url = current_url.split("&week=")[0]
                self.driver.get(f"{current_url}&week={self.week_number}")
                self.random_delay(0.5, 1.0)  # Уменьшенная задержка после перехода на неделю

                # Извлечение расписания
                try:
                    print("Извлекаем расписание...")
                    schedule_block = wait.until(ec.presence_of_element_located(
                        (By.CSS_SELECTOR, "ul.step.mb-5")
                    ))
                    html = schedule_block.get_attribute("innerHTML")
                    self.save_to_cache(html)
                    print(f"Успешно загружено с попытки {attempt}")
                    self.driver.quit()
                    return html
                except TimeoutException:
                    screenshot_path = f"schedule_error_{self.group_code}_week{self.week_number}_attempt{attempt}.png"
                    self.driver.save_screenshot(screenshot_path)
                    print(f"[Ошибка] Не найден блок расписания. Скриншот сохранён: {screenshot_path}")
                    raise TimeoutException("Блок с расписанием не найден.")

            except Exception as e:
                print(f"Попытка {attempt} не удалась: {e}")
                if attempt == max_attempts:
                    screenshot_path = f"schedule_error_{self.group_code}_week{self.week_number}_final.png"
                    try:
                        self.driver.save_screenshot(screenshot_path)
                        print(f"[Ошибка] Итоговый скриншот сохранён: {screenshot_path}")
                    except Exception as ex:
                        print(f"Ошибка при сохранении скриншота: {ex}")
                    raise Exception(f"Не удалось загрузить расписание после {max_attempts} попыток.")
            finally:
                if attempt == max_attempts:
                    self.driver.quit()

    def parse_schedule_html(self, html):
        """Парсинг HTML расписания."""
        soup = BeautifulSoup(html, 'html.parser')
        schedule_data = []
        
        # Отладочный вывод HTML для анализа структуры
        print("\n=== HTML структура расписания ===")
        print(html)
        print("===============================\n")
        
        # Ищем все дни недели
        days = soup.find_all('li', class_='step-item')
        if not days:
            print("Дни недели не найдены")
            return False
            
        print(f"\nНайдено {len(days)} дней недели")
        
        for day_item in days:
            try:
                # Извлекаем день недели и дату
                day_title = day_item.find('span', class_='step-title')
                if not day_title:
                    continue
                    
                day_text = day_title.text.strip()
                print(f"\nОбрабатываем день: {day_text}")
                
                # --- Фикс: сохраняем только полное название дня недели ---
                day_map = {
                    'Пн': 'Понедельник',
                    'Вт': 'Вторник',
                    'Ср': 'Среда',
                    'Чт': 'Четверг',
                    'Пт': 'Пятница',
                    'Сб': 'Суббота',
                    'Вс': 'Воскресенье'
                }
                day_short = day_text.split(',')[0].strip()
                day_full = day_map.get(day_short, day_short)
                
                # Ищем все занятия в этот день (теперь ищем div.mb-4)
                lessons = day_item.find_all('div', class_='mb-4')
                print(f"Найдено {len(lessons)} занятий в день {day_full}")
                
                for lesson in lessons:
                    try:
                        # Отладочный вывод структуры занятия
                        print(f"\n=== Структура занятия ===")
                        print(lesson.prettify())
                        print("===============================\n")
                        
                        # Название предмета
                        subject_elem = lesson.find('p', class_='fw-semi-bold')
                        if not subject_elem:
                            continue
                            
                        # Получаем полное название предмета
                        subject = subject_elem.text.strip()
                        
                        # Убираем тип занятия из названия
                        subject = subject.replace('ПЗ', '').replace('ЛК', '').replace('ЛР', '').strip()
                        
                        # Время занятия
                        time_elem = lesson.find('li', class_='list-inline-item')
                        if not time_elem:
                            continue
                            
                        time = time_elem.text.strip()
                        
                        # Тип занятия
                        type_elem = lesson.find('span', class_='badge')
                        lesson_type = type_elem.get('data-bs-original-title', '') if type_elem else ""
                        # Сокращаем тип занятия
                        type_map = {
                            'Лекция': 'ЛК',
                            'Практическое занятие': 'ПЗ',
                            'Лабораторная работа': 'ЛР'
                        }
                        lesson_type = type_map.get(lesson_type, lesson_type)
                        
                        # Аудитория (исправленный поиск)
                        room = ""
                        room_elem = lesson.select_one('li.list-inline-item:has(i.fad.fa-map-marker-alt)')
                        if room_elem:
                            # Получаем текст после иконки
                            room = room_elem.get_text(strip=True)
                            # Убираем иконку и лишние пробелы
                            room = ' '.join(room.split())
                            print(f"Найдена аудитория: {room}")  # Отладочный вывод
                        
                        # Преподаватель (исправленный поиск)
                        teacher = ""
                        teacher_elems = lesson.find_all('li', class_='list-inline-item')
                        for elem in teacher_elems:
                            if elem.find('a', class_='text-body'):
                                full_name = elem.text.strip()
                                # Сокращаем имя и отчество до инициалов
                                name_parts = full_name.split()
                                if len(name_parts) >= 3:
                                    teacher = f"{name_parts[0]} {name_parts[1][0]}.{name_parts[2][0]}."
                                else:
                                    teacher = full_name
                                break
                        
                        # Формируем тип занятия с преподавателем
                        type_with_teacher = lesson_type
                        if teacher:
                            type_with_teacher = f"{lesson_type} | {teacher}"
                        
                        # Добавляем данные в список
                        schedule_data.append({
                            'day': day_full,
                            'time': time,
                            'subject': subject,
                            'teacher': teacher,
                            'room': room,
                            'type': type_with_teacher,
                            'group': self.group_code
                        })
                        
                        print(f"Добавлено занятие: {day_full} {time} - {subject} (ауд. {room}, преп. {teacher})")
                        
                    except Exception as e:
                        print(f"Ошибка при обработке занятия: {e}")
                        continue
                
            except Exception as e:
                print(f"Ошибка при обработке дня: {e}")
                continue
        
        # Если расписание найдено, сохраняем в базу данных
        if schedule_data:
            print(f"\nВсего найдено {len(schedule_data)} занятий")
            for item in schedule_data:
                # Сначала создаем или получаем предмет
                subject = Subject.query.filter_by(subject_code=item['subject']).first()
                if not subject:
                    subject = Subject(subject_code=item['subject'])
                    db.session.add(subject)
                
                # Создаем запись в расписании
                schedule = Schedule(
                    day=item['day'],
                    time_slot=item['time'],
                    subject_code=item['subject'],
                    subject_type=item['type'],
                    room_number=item['room'],
                    group_code=item['group'],
                    week_num=self.week_number
                )
                db.session.add(schedule)
            db.session.commit()
            return True
        else:
            print("\nРасписание не найдено")
            return False
