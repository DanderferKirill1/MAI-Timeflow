// Конфигурация Google Calendar API
const CLIENT_ID = '583956306526-lebmvrldn2bnpqk2shm0eitptlkgau9r.apps.googleusercontent.com';
const API_KEY = 'AIzaSyAUn2euJe_P7FY79dGqVmV18txjgMPHzIw';
const DISCOVERY_DOC = 'https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest';
const SCOPES = 'https://www.googleapis.com/auth/calendar.events';

let tokenClient;
let gapiInited = false;
let gisInited = false;

// Инициализация Google API
function gapiLoaded() {
  gapi.load('client', initializeGapiClient);
}

async function initializeGapiClient() {
  await gapi.client.init({
    apiKey: API_KEY,
    discoveryDocs: [DISCOVERY_DOC],
  });
  gapiInited = true;
  maybeEnableButtons();
}

function gisLoaded() {
  tokenClient = google.accounts.oauth2.initTokenClient({
    client_id: CLIENT_ID,
    scope: SCOPES,
    callback: '', // Определяется позже
    prompt: 'consent'
  });
  gisInited = true;
  maybeEnableButtons();
}

function maybeEnableButtons() {
  if (gapiInited && gisInited) {
    document.getElementById('syncGoogleCalendar').disabled = false;
  }
}

// Функция для создания события в календаре
async function createCalendarEvent(event) {
  try {
    const response = await gapi.client.calendar.events.insert({
      'calendarId': 'primary',
      'resource': event
    });
    return response;
  } catch (err) {
    console.error('Ошибка при создании события:', err);
    throw err;
  }
}

// Функция для преобразования расписания в события календаря
function convertScheduleToEvents(schedule) {
  return schedule.map(lesson => ({
    'summary': lesson.subject,
    'location': lesson.room,
    'description': `Преподаватель: ${lesson.teacher}`,
    'start': {
      'dateTime': lesson.startTime,
      'timeZone': 'Europe/Moscow',
    },
    'end': {
      'dateTime': lesson.endTime,
      'timeZone': 'Europe/Moscow',
    },
  }));
}

// Функция для получения текущего расписания
async function getCurrentSchedule() {
  const selectedGroup = document.querySelector('.group-item.selected')?.textContent;
  if (!selectedGroup) {
    throw new Error('Пожалуйста, выберите группу');
  }

  const currentDate = new Date();
  const formattedDate = `${String(currentDate.getDate()).padStart(2, '0')}.${String(currentDate.getMonth() + 1).padStart(2, '0')}.${currentDate.getFullYear()}`;

  const response = await fetch('http://127.0.0.1:5000/api/schedule_week', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      group_code: selectedGroup,
      date: formattedDate
    }),
  });

  if (!response.ok) {
    throw new Error('Ошибка при получении расписания');
  }

  const scheduleData = await response.json();
  console.log('Полученные данные расписания:', scheduleData);
  
  // Преобразуем расписание в формат для Google Calendar
  const events = [];
  scheduleData.forEach(dayData => {
    console.log('Обработка дня:', dayData);
    
    if (!dayData.day || typeof dayData.day !== 'string') {
      console.error('Некорректный формат дня:', dayData.day);
      return;
    }

    try {
      const [dayName, dateStr] = dayData.day.split(', ');
      console.log('Разбор дня:', { dayName, dateStr });
      
      if (!dateStr) {
        console.error('Не удалось получить дату из строки:', dayData.day);
        return;
      }

      const [day, month] = dateStr.split(' ');
      console.log('Разбор даты:', { day, month });
      
      const months = {
        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
        'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
        'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
      };
      
      const year = new Date().getFullYear();
      const monthNum = months[month.toLowerCase()];
      const dayNum = parseInt(day);

      if (!monthNum || isNaN(dayNum)) {
        console.error('Некорректная дата:', { month, day });
        return;
      }

      dayData.lessons.forEach(lesson => {
        console.log('Обработка занятия:', lesson);
        
        if (!lesson.time) {
          console.error('Отсутствует время занятия:', lesson);
          return;
        }

        // Заменяем длинное тире на обычный дефис
        const normalizedTime = lesson.time.replace('–', '-');
        const [startTime, endTime] = normalizedTime.split(' - ');
        
        if (!startTime || !endTime) {
          console.error('Некорректный формат времени:', lesson.time);
          return;
        }

        const [startHour, startMinute] = startTime.split(':');
        const [endHour, endMinute] = endTime.split(':');

        const startDate = new Date(year, monthNum - 1, dayNum, parseInt(startHour), parseInt(startMinute));
        const endDate = new Date(year, monthNum - 1, dayNum, parseInt(endHour), parseInt(endMinute));

        events.push({
          subject: lesson.subject.replace(/\n\s+/g, ' ').trim(), // Убираем переносы строк и лишние пробелы
          room: lesson.room,
          teacher: lesson.teacher || lesson.type.split('|')[1]?.trim() || '', // Берем имя преподавателя из type, если teacher пустой
          startTime: startDate.toISOString(),
          endTime: endDate.toISOString()
        });
      });
    } catch (error) {
      console.error('Ошибка при обработке дня:', error);
    }
  });

  console.log('Сформированные события:', events);
  return events;
}

// Обработчик нажатия на кнопку синхронизации
document.getElementById('syncGoogleCalendar').addEventListener('click', async () => {
  try {
    // Получаем текущее расписание
    const schedule = await getCurrentSchedule();
    
    // Преобразуем расписание в формат событий календаря
    const events = convertScheduleToEvents(schedule);
    
    // Запрашиваем авторизацию
    tokenClient.callback = async (resp) => {
      if (resp.error !== undefined) {
        if (resp.error === 'popup_closed_by_user') {
          // Проверяем настройки уведомлений перед показом сообщения
          const settings = await getNotificationSettings();
          if (settings.push_notifications) {
            showToast('Авторизация была отменена', 'info');
          }
          return;
        }
        throw (resp);
      }
      
      try {
        // Создаем события в календаре
        for (const event of events) {
          await createCalendarEvent(event);
        }
        
        // Создаем уведомление о успешной синхронизации
        const notificationResponse = await fetch('http://127.0.0.1:5000/api/notifications', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({
            type: 'sync',
            subject_name: 'Google Calendar',
            message: 'Расписание успешно синхронизировано с Google Calendar'
          })
        });

        if (!notificationResponse.ok) {
          console.error('Ошибка при создании уведомления:', await notificationResponse.text());
        }
        
        // Проверяем настройки уведомлений перед показом сообщения
        const settings = await getNotificationSettings();
        if (settings.push_notifications) {
          showToast('Расписание успешно синхронизировано с Google Calendar!', 'success');
        }
      } catch (error) {
        console.error('Ошибка при создании событий:', error);
        const settings = await getNotificationSettings();
        if (settings.push_notifications) {
          showToast('Ошибка при создании событий в календаре', 'error');
        }
      }
    };
    
    if (gapi.client.getToken() === null) {
      tokenClient.requestAccessToken();
    } else {
      tokenClient.requestAccessToken({prompt: ''});
    }
  } catch (err) {
    console.error('Ошибка при синхронизации:', err);
    const settings = await getNotificationSettings();
    if (settings.push_notifications) {
      showToast('Произошла ошибка при синхронизации с Google Calendar', 'error');
    }
  }
});

// Функция для получения настроек уведомлений
async function getNotificationSettings() {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/notification-settings', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Ошибка при получении настроек уведомлений');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Ошибка при получении настроек уведомлений:', error);
    return { push_notifications: true }; // По умолчанию включены
  }
}

// Функция для отображения уведомлений
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.remove();
  }, 3000);
}

// Загружаем Google API
const script1 = document.createElement('script');
script1.src = 'https://apis.google.com/js/api.js';
script1.onload = gapiLoaded;
document.head.appendChild(script1);

const script2 = document.createElement('script');
script2.src = 'https://accounts.google.com/gsi/client';
script2.onload = gisLoaded;
document.head.appendChild(script2); 