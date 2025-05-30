import { setupSelectListeners } from './selects.js';

document.addEventListener("DOMContentLoaded", () => {
  const showBtn = document.querySelector(".show-timetable");
  const wrapper = document.getElementById("timetable-wrapper");
  const timetable = document.getElementById("timetable");
  const prevWeekBtn = document.querySelector(".nav-btn-prev");
  const nextWeekBtn = document.querySelector(".nav-btn-next");

  let selectedGroup = null;
  let currentDate = new Date();

  // Маппинг значений для правильного запроса
  const instituteMap = {
    "1": "Институт №1",
    "2": "Институт №2",
    "3": "Институт №3",
    "4": "Институт №4",
    "5": "Институт №5",
    "6": "Институт №6",
    "7": "Институт №7",
    "8": "Институт №8"
  };

  const levelNames = {
    "БВ": "Базовое высшее образование",
    "СВ": "Специализированное высшее образование",
    "А": "Аспирантура"
  };

  // Форматирование даты в формат DD.MM.YYYY
  function formatDate(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
  }

  // Загрузка расписания
  async function loadSchedule() {
    if (!selectedGroup) {
      alert('Пожалуйста, выберите группу');
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:5000/api/schedule_week', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          group_code: selectedGroup,
          date: formatDate(currentDate)
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        if (response.status === 404) {
          // Если расписание не найдено, показываем пустую неделю
          const weekStart = new Date(currentDate);
          weekStart.setDate(currentDate.getDate() - currentDate.getDay() + 1);
          
          const result = [];
          for (let i = 0; i < 7; i++) {
            const date = new Date(weekStart);
            date.setDate(weekStart.getDate() + i);
            const dayName = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'][i];
            result.push({
              day: `${dayName}, ${date.getDate()} ${getMonthName(date.getMonth() + 1)}`,
              lessons: []
            });
          }
          displaySchedule(result);
        } else {
          timetable.innerHTML = `<p class="error">${errorData.error || 'Ошибка при загрузке расписания'}</p>`;
        }
        return;
      }

      const scheduleData = await response.json();
      displaySchedule(scheduleData);
    } catch (error) {
      console.error('Error:', error);
      timetable.innerHTML = '<p class="error">Ошибка при загрузке расписания. Пожалуйста, попробуйте позже.</p>';
    }
  }

  // Отображение расписания
  function displaySchedule(scheduleData) {
    timetable.innerHTML = "";

    // Показываем кнопки навигации
    prevWeekBtn.style.display = 'flex';
    nextWeekBtn.style.display = 'flex';

    // Создаем карточки для всех дней недели
    const allDays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'];
    
    // Преобразуем данные расписания в объект для удобного доступа
    const scheduleMap = {};
    let weekStartDate = null;
    
    scheduleData.forEach(dayData => {
      const [dayName, dateStr] = dayData.day.split(', ');
      scheduleMap[dayName] = dayData;
      
      // Определяем дату понедельника
      if (dayName === 'Понедельник') {
        const [day, month] = dateStr.split(' ');
        weekStartDate = new Date(new Date().getFullYear(), getMonthNumber(month) - 1, parseInt(day));
      }
    });

    // Создаем контейнер для карточек дней
    const daysContainer = document.createElement("div");
    daysContainer.className = "days-container";

    allDays.forEach((dayName, index) => {
      const dayDiv = document.createElement("div");
      dayDiv.className = "day-card";

      const title = document.createElement("h3");
      title.className = "day-card-title";
      
      // Получаем данные дня из расписания
      const dayData = scheduleMap[dayName];
      let dateStr = '';
      
      if (weekStartDate) {
        const currentDate = new Date(weekStartDate);
        currentDate.setDate(weekStartDate.getDate() + index);
        dateStr = `${currentDate.getDate()} ${getMonthName(currentDate.getMonth() + 1)}`;
      }
      
      // Создаем элемент для даты
      const dateSpan = document.createElement("span");
      dateSpan.className = "day-card-date";
      dateSpan.textContent = dateStr;
      
      // Создаем элемент для дня недели
      const daySpan = document.createElement("span");
      daySpan.className = "day-card-name";
      daySpan.textContent = dayName;

      // Собираем заголовок
      title.appendChild(dateSpan);
      title.appendChild(daySpan);
      dayDiv.appendChild(title);

      // Если нет пар или это выходной
      if (!dayData || !dayData.lessons || dayData.lessons.length === 0) {
        dayDiv.classList.add("day-card-empty");
      } else {
        const lessonsContainer = document.createElement("div");
        lessonsContainer.className = "lessons-container";

        dayData.lessons.forEach((lesson) => {
          const lessonDiv = document.createElement("div");
          lessonDiv.className = "lesson";

          // Время
          const timeDiv = document.createElement("div");
          timeDiv.className = "lesson-time";
          timeDiv.textContent = lesson.time;
          lessonDiv.appendChild(timeDiv);

          // Основная информация
          const mainInfoDiv = document.createElement("div");
          mainInfoDiv.className = "lesson-main-info";

          // Название предмета
          const subjectDiv = document.createElement("div");
          subjectDiv.className = "lesson-subject";
          subjectDiv.textContent = lesson.subject;
          subjectDiv.setAttribute('data-full-title', lesson.subject);
          
          // Проверяем, обрезан ли текст после рендеринга
          requestAnimationFrame(() => {
            if (subjectDiv.scrollWidth > subjectDiv.clientWidth) {
              subjectDiv.classList.add('truncated');
            }
          });
          
          mainInfoDiv.appendChild(subjectDiv);

          // Дополнительная информация (преподаватель и тип занятия)
          const additionalInfo = document.createElement("div");
          additionalInfo.className = "lesson-additional-info";
          
          const teacherAndType = [];
          if (lesson.teacher) teacherAndType.push(lesson.teacher);
          if (lesson.type) teacherAndType.push(lesson.type);
          
          additionalInfo.textContent = teacherAndType.join(' | ');
          mainInfoDiv.appendChild(additionalInfo);

          lessonDiv.appendChild(mainInfoDiv);

          // Аудитория
          const roomDiv = document.createElement("div");
          roomDiv.className = "lesson-room";
          roomDiv.textContent = lesson.room;
          lessonDiv.appendChild(roomDiv);

          lessonsContainer.appendChild(lessonDiv);
        });

        dayDiv.appendChild(lessonsContainer);
      }

      daysContainer.appendChild(dayDiv);
    });

    // Добавляем контейнер с днями
    timetable.appendChild(daysContainer);
  }

  // Вспомогательная функция для получения номера месяца
  function getMonthNumber(monthName) {
    const months = {
      'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
      'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
      'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
    };
    return months[monthName.toLowerCase()];
  }

  // Вспомогательная функция для получения названия месяца
  function getMonthName(monthNumber) {
    const months = [
      'января', 'февраля', 'марта', 'апреля',
      'мая', 'июня', 'июля', 'августа',
      'сентября', 'октября', 'ноября', 'декабря'
    ];
    return months[monthNumber - 1];
  }

  // Обработчик выбора группы
  function handleGroupSelect(group) {
    selectedGroup = group;
  }

  // Подписываемся на событие выбора группы
  document.addEventListener('groupSelected', (event) => {
    handleGroupSelect(event.detail);
  });

  // Настройка обработчиков событий
  setupSelectListeners();

  showBtn.addEventListener("click", () => {
    if (selectedGroup) {
      wrapper.classList.remove("hidden");
      loadSchedule();
    } else {
      alert('Пожалуйста, выберите группу');
    }
  });

  // Обработка переключения недель
  prevWeekBtn.addEventListener('click', async () => {
    try {
      currentDate.setDate(currentDate.getDate() - 7);
      const response = await fetch('http://127.0.0.1:5000/api/schedule_week', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          group_code: selectedGroup,
          date: formatDate(currentDate)
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        if (response.status === 404) {
          // Если расписание не найдено, показываем пустую неделю
          const weekStart = new Date(currentDate);
          weekStart.setDate(currentDate.getDate() - currentDate.getDay() + 1);
          
          const result = [];
          for (let i = 0; i < 7; i++) {
            const date = new Date(weekStart);
            date.setDate(weekStart.getDate() + i);
            const dayName = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'][i];
            result.push({
              day: `${dayName}, ${date.getDate()} ${getMonthName(date.getMonth() + 1)}`,
              lessons: []
            });
          }
          displaySchedule(result);
        } else {
          throw new Error(errorData.error || 'Ошибка при загрузке расписания');
        }
        return;
      }

      const scheduleData = await response.json();
      displaySchedule(scheduleData);
    } catch (error) {
      console.error('Error:', error);
      timetable.innerHTML = '<p class="error">Ошибка при загрузке расписания. Пожалуйста, попробуйте позже.</p>';
    }
  });

  nextWeekBtn.addEventListener('click', async () => {
    try {
      currentDate.setDate(currentDate.getDate() + 7);
      const response = await fetch('http://127.0.0.1:5000/api/schedule_week', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          group_code: selectedGroup,
          date: formatDate(currentDate)
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        if (response.status === 404) {
          // Если расписание не найдено, показываем пустую неделю
          const weekStart = new Date(currentDate);
          weekStart.setDate(currentDate.getDate() - currentDate.getDay() + 1);
          
          const result = [];
          for (let i = 0; i < 7; i++) {
            const date = new Date(weekStart);
            date.setDate(weekStart.getDate() + i);
            const dayName = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'][i];
            result.push({
              day: `${dayName}, ${date.getDate()} ${getMonthName(date.getMonth() + 1)}`,
              lessons: []
            });
          }
          displaySchedule(result);
        } else {
          throw new Error(errorData.error || 'Ошибка при загрузке расписания');
        }
        return;
      }

      const scheduleData = await response.json();
      displaySchedule(scheduleData);
    } catch (error) {
      console.error('Error:', error);
      timetable.innerHTML = '<p class="error">Ошибка при загрузке расписания. Пожалуйста, попробуйте позже.</p>';
    }
  });

  // Добавляем проверку обрезанных названий после загрузки расписания
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes.length) {
        checkTruncatedTitles();
      }
    });
  });

  observer.observe(document.getElementById('timetable'), { 
    childList: true, 
    subtree: true 
  });
});

// Проверяем при изменении размера окна
window.addEventListener('resize', checkTruncatedTitles);

function checkTruncatedTitles() {
  const subjects = document.querySelectorAll('.lesson-subject');
  
  subjects.forEach(subject => {
    if (subject.offsetWidth < subject.scrollWidth) {
      subject.classList.add('truncated');
      subject.setAttribute('data-full-title', subject.textContent);
    } else {
      subject.classList.remove('truncated');
      subject.removeAttribute('data-full-title');
    }
  });
}
