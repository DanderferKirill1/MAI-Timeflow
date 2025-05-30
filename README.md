# MAI TimeFlow
MAI Timeflow - веб-приложение для просмотра расписания МАИ.
## Краткое описание
Наша команда разрабатывает веб-приложение для работы с университетским расписанием. Сейчас мы реализуем базовый функционал, который обеспечит быстрый доступ к актуальной информации о занятиях и изменениях в расписании. Параллельно мы работаем над расширением возможностей проекта: добавляем персонализированные уведомления, фильтры по группам и другие удобные инструменты для студентов и преподавателей.
## Цели проекта
_Регистрация и вход:_
  - Регистрация с использованием группы студента, электронной почты и пароля
  - Хеширование всех персональных данных, включая пароли, для обеспечения безопасности
  - Вход в систему с проверкой учетных данных

_Организация корректного функционирования базы данных:_
   - База данных для хранения информации о пользователях и расписании групп.
   - Парсинг расписания с сайта МАИ с помошью CLI-утилиты

_Создание раздела "Избранное":_
   - Раздел для добавления расписания выбранных групп.

_Создание формы добавления занятий:_
   - Возможность добавления занятий, отсутствующих в расписании через специальную форму.
## Технологический стек
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white) ![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=flat-square&logo=selenium&logoColor=white) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) ![Node.js](https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=node.js&logoColor=white) 
## Запуск проекта
1. Установите Node.js с сайта https://nodejs.org/en
2.  Создайте в папке backend файл .env и впишите ключи:
	```env
	SECRET_KEY=
	JWT_SECRET_KEY=
	```

3. В корне проекта выполните команды:
   ```bash
	npm install
	```

   ```bash
	npm run setup
	```

	```bash
	npm run dev
	```
## Участники проекта:
  - Нифантьев Сергей - backend
  - Яковлева Дарья - frontend
  - Дандерфер Кирилл - teamlead, design, frontend
  - Чакал Никита - backend
  - Газиев Руслан - system analyst

## Источники:

- Figma: [тык](https://www.figma.com/design/sYTVJIdrhhBzn7Rv091nH7/MAI-TIMEFLOW?node-id=101-71&t=032pkhkwUch6qzJi-1)
- Yougile: [тык](https://ru.yougile.com/board/bc5w2grej0oz)
