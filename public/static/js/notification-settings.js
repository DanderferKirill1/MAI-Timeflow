// Функция для загрузки настроек уведомлений
async function loadNotificationSettings() {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/notification-settings', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Ошибка при получении настроек уведомлений');
    }
    
    const settings = await response.json();
    
    // Обновляем состояние переключателей
    document.getElementById('scheduleChangesToggle').checked = settings.schedule_changes;
    document.getElementById('lessonRemindersToggle').checked = settings.lesson_reminders;
    document.getElementById('reminderTimeSelect').value = settings.reminder_time;
    document.getElementById('pushNotificationsToggle').checked = settings.push_notifications;
    document.getElementById('emailNotificationsToggle').checked = settings.email_notifications;
    document.getElementById('telegramNotificationsToggle').checked = settings.telegram_notifications;
    
  } catch (error) {
    console.error('Ошибка при загрузке настроек уведомлений:', error);
  }
}

// Функция для обновления настроек уведомлений
async function updateNotificationSettings(settings) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/notification-settings', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(settings)
    });
    
    if (!response.ok) {
      throw new Error('Ошибка при обновлении настроек уведомлений');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Ошибка при обновлении настроек уведомлений:', error);
    throw error;
  }
}

// Функция для форматирования даты
function formatNotificationDate(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  
  if (days === 0) {
    return `Сегодня в ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  } else if (days === 1) {
    return `Вчера в ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  } else {
    return `${date.getDate().toString().padStart(2, '0')}.${(date.getMonth() + 1).toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  }
}

// Функция для получения иконки по типу уведомления
function getNotificationIcon(type) {
  switch (type) {
    case 'sync':
      return '/assets/images/sync.svg';
    case 'changed':
      return '/assets/images/changed.svg';
    case 'cancelled':
      return '/assets/images/cancelled.svg';
    default:
      return '/assets/images/notification.svg';
  }
}

// Функция для загрузки истории уведомлений
async function loadNotificationHistory() {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/notifications', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Ошибка при получении истории уведомлений');
    }
    
    const notifications = await response.json();
    console.log('Полученные уведомления:', notifications);
    
    const historyContainer = document.getElementById('notificationsHistory');
    historyContainer.innerHTML = '';
    
    // Фильтруем только непрочитанные уведомления
    const unreadNotifications = notifications.filter(notification => !notification.is_read);
    
    unreadNotifications.forEach(notification => {
      console.log('Обработка уведомления:', notification);
      
      const notificationCard = document.createElement('div');
      notificationCard.className = `notification-card ${notification.is_read ? 'read' : 'unread'}`;
      
      // Проверяем наличие ID
      if (!notification.notification_id) {
        console.error('Уведомление без ID:', notification);
        return;
      }
      
      notificationCard.innerHTML = `
        <div class="notification-icon ${notification.type}">
          <img src="${getNotificationIcon(notification.type)}" alt="${notification.type}">
        </div>
        <div class="notification-content">
          <p class="notification-text">${notification.message}</p>
        </div>
        <div class="notification-actions">
          <div class="notification-time">${formatNotificationDate(notification.created_at)}</div>
          ${!notification.is_read ? `
            <button class="mark-as-read-btn" data-notification-id="${notification.notification_id}" onclick="markNotificationAsRead(${notification.notification_id})">
              <img src="/assets/images/check-double.svg" alt="Отметить как прочитанное">
            </button>
          ` : ''}
        </div>
      `;
      
      historyContainer.appendChild(notificationCard);
    });
    
  } catch (error) {
    console.error('Ошибка при загрузке истории уведомлений:', error);
  }
}

// Функция для отметки уведомления как прочитанного
async function markNotificationAsRead(notificationId) {
  console.log('Попытка отметить уведомление как прочитанное. ID:', notificationId);
  
  if (!notificationId) {
    console.error('ID уведомления не указан');
    return;
  }

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/notifications/${notificationId}/read`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Ошибка при отметке уведомления как прочитанного');
    }
    
    const result = await response.json();
    console.log('Ответ сервера:', result);
    
    // Находим и скрываем уведомление
    const notificationCard = document.querySelector(`[data-notification-id="${notificationId}"]`).closest('.notification-card');
    if (notificationCard) {
      notificationCard.style.opacity = '0';
      setTimeout(() => {
        notificationCard.style.display = 'none';
      }, 300); // Время должно совпадать с CSS transition
    }
    
  } catch (error) {
    console.error('Ошибка при отметке уведомления:', error);
  }
}

// Обработчики событий для переключателей
document.addEventListener('DOMContentLoaded', () => {
  // Загружаем настройки при загрузке страницы
  loadNotificationSettings();
  loadNotificationHistory();
  
  // Обработчик для переключателя изменений в расписании
  document.getElementById('scheduleChangesToggle').addEventListener('change', async (e) => {
    try {
      await updateNotificationSettings({ schedule_changes: e.target.checked });
    } catch (error) {
      e.target.checked = !e.target.checked; // Возвращаем предыдущее состояние при ошибке
    }
  });
  
  // Обработчик для переключателя напоминаний о парах
  document.getElementById('lessonRemindersToggle').addEventListener('change', async (e) => {
    try {
      await updateNotificationSettings({ lesson_reminders: e.target.checked });
    } catch (error) {
      e.target.checked = !e.target.checked;
    }
  });
  
  // Обработчик для выбора времени напоминания
  document.getElementById('reminderTimeSelect').addEventListener('change', async (e) => {
    try {
      await updateNotificationSettings({ reminder_time: parseInt(e.target.value) });
    } catch (error) {
      // Возвращаем предыдущее значение при ошибке
      const settings = await loadNotificationSettings();
      e.target.value = settings.reminder_time;
    }
  });
  
  // Обработчик для переключателя push-уведомлений
  document.getElementById('pushNotificationsToggle').addEventListener('change', async (e) => {
    try {
      await updateNotificationSettings({ push_notifications: e.target.checked });
    } catch (error) {
      e.target.checked = !e.target.checked;
    }
  });
  
  // Обработчик для переключателя email-уведомлений
  document.getElementById('emailNotificationsToggle').addEventListener('change', async (e) => {
    try {
      await updateNotificationSettings({ email_notifications: e.target.checked });
    } catch (error) {
      e.target.checked = !e.target.checked;
    }
  });
  
  // Обработчик для переключателя telegram-уведомлений
  document.getElementById('telegramNotificationsToggle').addEventListener('change', async (e) => {
    try {
      await updateNotificationSettings({ telegram_notifications: e.target.checked });
    } catch (error) {
      e.target.checked = !e.target.checked;
    }
  });
}); 