document.addEventListener('DOMContentLoaded', function() {
    // Get all navigation items and sections
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.section-content');

    // Function to switch section
    function switchSection(sectionId) {
        // Remove active class from all nav items and sections
        navItems.forEach(nav => nav.classList.remove('active'));
        sections.forEach(section => section.classList.remove('active'));

        // Add active class to corresponding nav item and section
        const targetNav = document.querySelector(`[data-section="${sectionId}"]`);
        if (targetNav) {
            targetNav.classList.add('active');
        }
        const targetSection = document.getElementById(`${sectionId}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
            
            // Если это раздел уведомлений, добавляем классы для стилей
            if (sectionId === 'notifications') {
                console.log('Switching to notifications section');
                
                const notificationsContent = targetSection.querySelector('.notifications-content');
                const notificationsGrid = targetSection.querySelector('.notifications-grid');
                const notificationsSettings = targetSection.querySelector('.notifications-settings');
                const deliveryMethods = targetSection.querySelector('.delivery-methods');
                
                console.log('Elements found:', {
                    notificationsContent,
                    notificationsGrid,
                    notificationsSettings,
                    deliveryMethods
                });
                
                if (notificationsContent) {
                    notificationsContent.classList.add('active');
                    console.log('Applied styles to notificationsContent:', window.getComputedStyle(notificationsContent));
                }
                if (notificationsGrid) {
                    notificationsGrid.classList.add('active');
                    console.log('Applied styles to notificationsGrid:', window.getComputedStyle(notificationsGrid));
                }
                if (notificationsSettings) {
                    notificationsSettings.classList.add('active');
                    console.log('Applied styles to notificationsSettings:', window.getComputedStyle(notificationsSettings));
                }
                if (deliveryMethods) {
                    deliveryMethods.classList.add('active');
                    console.log('Applied styles to deliveryMethods:', window.getComputedStyle(deliveryMethods));
                }
                
                // Проверяем загруженные стили
                const styles = Array.from(document.styleSheets).map(sheet => {
                    try {
                        return Array.from(sheet.cssRules).map(rule => rule.cssText);
                    } catch (e) {
                        return [];
                    }
                }).flat();
                
                console.log('Loaded CSS rules:', styles);
                
                loadNotifications();
            }
        }
    }

    // Check URL parameters for section
    const urlParams = new URLSearchParams(window.location.search);
    const sectionParam = urlParams.get('section');
    if (sectionParam) {
        switchSection(sectionParam);
    }

    // Add click event to each navigation item
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-section');
            switchSection(sectionId);
            
            // Update URL without reloading the page
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.set('section', sectionId);
            window.history.pushState({}, '', newUrl);
        });
    });

    // Функция для загрузки данных профиля
    async function loadProfileData() {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                window.location.href = '/';
                return;
            }

            const response = await fetch('/api/profile', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                
                // Заполняем поля формы данными
                document.querySelector('.profile-section-info h2').textContent = `${data.first_name} ${data.last_name}`;
                document.querySelector('.profile-section-email').textContent = data.email;
                
                document.getElementById('firstName').value = data.first_name || '';
                document.getElementById('lastName').value = data.last_name || '';
                document.getElementById('group').value = data.group_code || '';
                document.getElementById('gender').value = data.gender || '';
                
                // Обновляем email в привязанных данных
                const linkedEmail = document.querySelector('.profile-linked-item .linked-value');
                if (linkedEmail) {
                    linkedEmail.textContent = data.email;
                }
            } else if (response.status === 401) {
                // Если токен недействителен, перенаправляем на главную
                window.location.href = '/';
            } else {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Ошибка при загрузке данных профиля');
            }
        } catch (error) {
            console.error('Error loading profile data:', error);
            showToast(error.message || 'Ошибка при загрузке данных профиля', 'error');
        }
    }

    // Функция для обновления данных профиля
    async function updateProfile(formData) {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('/api/profile/edit', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const data = await response.json();
                showToast('Профиль успешно обновлен', 'success');
                // Перезагружаем данные профиля с сервера
                await loadProfileData();
            } else {
                const data = await response.json();
                showToast(data.error || 'Ошибка при обновлении профиля', 'error');
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            showToast('Ошибка при обновлении профиля', 'error');
        }
    }

    let isEditingMode = false;

    // Обработчик кнопки редактирования
    const editButton = document.getElementById('editButton');
    if (editButton) {
        editButton.addEventListener('click', async function() {
            const inputs = document.querySelectorAll('.profile-form-input:not(.password-input):not(#group), .profile-form-select');
            
            if (!isEditingMode) {
                // Включаем режим редактирования
                inputs.forEach(input => {
                    input.disabled = false;
                });
                this.textContent = 'Сохранить';
                this.classList.add('save-mode');
                isEditingMode = true;
            } else {
                // Собираем данные формы
                const formData = {
                    first_name: document.getElementById('firstName').value,
                    last_name: document.getElementById('lastName').value,
                    group_code: document.getElementById('group').value,
                    gender: document.getElementById('gender').value
                };
                
                // Отправляем данные на сервер
                await updateProfile(formData);
                
                // Возвращаем в режим просмотра
            inputs.forEach(input => {
                    input.disabled = true;
                });
                this.textContent = 'Редактировать';
                this.classList.remove('save-mode');
                isEditingMode = false;
            }
        });
    }

    // Функция для отображения уведомлений
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    // Обработчик кнопки выхода
    const logoutButton = document.querySelector('.profile-logout-btn');
    if (logoutButton) {
        logoutButton.addEventListener('click', async function() {
            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch('/api/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    localStorage.removeItem('access_token');
                    window.location.href = '/';
                }
            } catch (error) {
                console.error('Error during logout:', error);
                showToast('Ошибка при выходе из системы', 'error');
            }
        });
    }

    // Загружаем данные профиля при загрузке страницы
    loadProfileData();

    // Загружаем уведомления при загрузке страницы, если мы на вкладке уведомлений
    if (sectionParam === 'notifications') {
        loadNotifications();
    }

    async function updateSessions() {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                console.error('Токен не найден');
                return;
            }

            // Обновляем текущую сессию
            const currentSessionResponse = await fetch('http://127.0.0.1:5000/api/sessions/current', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });

            if (!currentSessionResponse.ok) {
                throw new Error('Ошибка при обновлении текущей сессии');
            }

            // Получаем все сессии
            const sessionsResponse = await fetch('http://127.0.0.1:5000/api/sessions', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });

            if (!sessionsResponse.ok) {
                throw new Error('Ошибка при получении списка сессий');
            }

            const sessions = await sessionsResponse.json();
            const sessionsList = document.querySelector('.sessions-list');
            
            if (!sessionsList) {
                console.error('Элемент .sessions-list не найден');
                return;
            }

            // Очищаем список сессий
            sessionsList.innerHTML = '';

            if (sessions.length === 0) {
                sessionsList.innerHTML = '<div class="no-sessions">Нет активных сессий</div>';
                return;
            }

            // Добавляем каждую сессию в список
            sessions.forEach(session => {
                const sessionElement = document.createElement('div');
                sessionElement.className = 'session-item';
                
                // Определяем иконку в зависимости от ОС
                let osIcon = 'computer.svg';
                if (session.os_info.toLowerCase().includes('windows')) {
                    osIcon = 'windows.svg';
                } else if (session.os_info.toLowerCase().includes('mac')) {
                    osIcon = 'apple.svg';
                } else if (session.os_info.toLowerCase().includes('linux')) {
                    osIcon = 'linux.svg';
                }

                sessionElement.innerHTML = `
                    <div class="session-info">
                        <img src="/assets/images/${osIcon}" alt="${session.os_info}" class="session-icon">
                        <div class="session-details">
                            <div class="session-os">${session.os_info}</div>
                            <div class="session-ip">IP: ${session.ip_address}</div>
                            <div class="session-time">${formatLastActivity(session.last_activity)}</div>
                        </div>
                    </div>
                `;
                
                sessionsList.appendChild(sessionElement);
            });
        } catch (error) {
            console.error('Ошибка при обновлении сессий:', error);
            const sessionsList = document.querySelector('.sessions-list');
            if (sessionsList) {
                sessionsList.innerHTML = '<div class="no-sessions">Ошибка при загрузке сессий</div>';
            }
        }
    }

    function formatLastActivity(dateStr) {
        // Преобразуем строку даты в объект Date
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;
        
        // Получаем локальное время с учетом часового пояса
        const localHours = date.getHours() + 3; // Добавляем 3 часа для московского времени
        const localMinutes = date.getMinutes();
        
        // Если прошло меньше суток
        if (diff < 24 * 60 * 60 * 1000) {
            return `Сегодня в ${localHours.toString().padStart(2, '0')}:${localMinutes.toString().padStart(2, '0')}`;
        }
        
        // Если прошло меньше двух суток
        if (diff < 48 * 60 * 60 * 1000) {
            return `Вчера в ${localHours.toString().padStart(2, '0')}:${localMinutes.toString().padStart(2, '0')}`;
        }
        
        // В остальных случаях показываем полную дату
        return date.toLocaleDateString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZone: 'Europe/Moscow' // Явно указываем часовой пояс
        });
    }

    // Функция для изменения пароля
    async function changePassword(oldPassword, newPassword) {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                window.location.href = '/';
                return;
            }

            const response = await fetch('http://127.0.0.1:5000/api/profile/change-password', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    old_password: oldPassword,
                    new_password: newPassword
                })
            });

            const data = await response.json();

            if (response.ok) {
                showToast('Пароль успешно изменен', 'success');
                // Очищаем поля ввода
                document.querySelectorAll('.safety-form input[type="password"]').forEach(input => {
                    input.value = '';
                });
        } else {
                throw new Error(data.error || 'Ошибка при изменении пароля');
            }
        } catch (error) {
            console.error('Error changing password:', error);
            showToast(error.message || 'Ошибка при изменении пароля', 'error');
        }
    }

    // Обработчик кнопки изменения пароля
    const changePasswordBtn = document.querySelector('.change-password-btn');
    if (changePasswordBtn) {
        changePasswordBtn.addEventListener('click', async function() {
            const oldPassword = document.querySelector('.safety-form .form-group:nth-child(1) input').value;
            const newPassword = document.querySelector('.safety-form .form-group:nth-child(2) input').value;
            const confirmPassword = document.querySelector('.safety-form .form-group:nth-child(3) input').value;

            // Проверяем, что все поля заполнены
            if (!oldPassword || !newPassword || !confirmPassword) {
                showToast('Пожалуйста, заполните все поля', 'error');
                return;
            }

            // Проверяем, что новый пароль и подтверждение совпадают
            if (newPassword !== confirmPassword) {
                showToast('Новый пароль и подтверждение не совпадают', 'error');
                return;
            }

            // Проверяем длину нового пароля
            if (newPassword.length < 8) {
                showToast('Новый пароль должен содержать минимум 8 символов', 'error');
                return;
            }

            await changePassword(oldPassword, newPassword);
        });
    }

    // Обновляем сессии при загрузке страницы
    updateSessions();
    // Обновляем сессии каждые 5 минут
    setInterval(updateSessions, 5 * 60 * 1000);

    // Функция для загрузки уведомлений
    async function loadNotifications() {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                console.error('Токен не найден');
                return;
            }

            const response = await fetch('/api/notifications', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Ошибка при загрузке уведомлений');
            }

            const notifications = await response.json();
            const notificationsHistory = document.querySelector('.notifications-history');
            
            if (!notificationsHistory) {
                console.error('Элемент .notifications-history не найден');
                return;
            }

            // Очищаем список уведомлений
            notificationsHistory.innerHTML = '';

            if (notifications.length === 0) {
                notificationsHistory.innerHTML = '<div class="no-notifications">Нет уведомлений</div>';
                return;
            }

            // Добавляем каждое уведомление в список
            notifications.forEach(notification => {
                const notificationElement = document.createElement('div');
                notificationElement.className = `notification-item ${notification.is_read ? 'read' : 'unread'}`;
                
                // Определяем иконку в зависимости от типа уведомления
                let icon = 'info.svg';
                if (notification.type === 'cancelled') {
                    icon = 'cancel.svg';
                } else if (notification.type === 'changed') {
                    icon = 'change.svg';
                }

                notificationElement.innerHTML = `
                    <div class="notification-content">
                        <img src="/assets/images/${icon}" alt="${notification.type}" class="notification-icon">
                        <div class="notification-details">
                            <h3>${notification.subject_name}</h3>
                            <p>${notification.message}</p>
                            <span class="notification-time">${formatNotificationTime(notification.created_at)}</span>
                        </div>
                    </div>
                `;
                
                notificationsHistory.appendChild(notificationElement);
            });
        } catch (error) {
            console.error('Ошибка при загрузке уведомлений:', error);
            const notificationsHistory = document.querySelector('.notifications-history');
            if (notificationsHistory) {
                notificationsHistory.innerHTML = '<div class="no-notifications">Ошибка при загрузке уведомлений</div>';
            }
        }
    }

    // Функция для форматирования времени уведомления
    function formatNotificationTime(dateStr) {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;
        
        // Получаем локальное время с учетом часового пояса
        const localHours = date.getHours() + 3; // Добавляем 3 часа для московского времени
        const localMinutes = date.getMinutes();
        
        // Если прошло меньше часа
        if (diff < 60 * 60 * 1000) {
            const minutes = Math.floor(diff / (60 * 1000));
            return `${minutes} минут назад`;
        }
        
        // Если прошло меньше суток
        if (diff < 24 * 60 * 60 * 1000) {
            return `Сегодня в ${localHours.toString().padStart(2, '0')}:${localMinutes.toString().padStart(2, '0')}`;
        }
        
        // Если прошло меньше двух суток
        if (diff < 48 * 60 * 60 * 1000) {
            return `Вчера в ${localHours.toString().padStart(2, '0')}:${localMinutes.toString().padStart(2, '0')}`;
        }
        
        // В остальных случаях показываем полную дату
        return date.toLocaleDateString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZone: 'Europe/Moscow'
        });
    }

    // Загружаем уведомления при открытии раздела
    document.querySelector('[data-section="notifications"]').addEventListener('click', () => {
        loadNotifications();
    });

    // Загружаем уведомления каждые 5 минут
    setInterval(loadNotifications, 5 * 60 * 1000);

    function initializeSectionStyles() {
        const notificationsSection = document.getElementById('notifications-section');
        if (notificationsSection) {
            const notificationsContent = notificationsSection.querySelector('.notifications-content');
            const notificationsGrid = notificationsSection.querySelector('.notifications-grid');
            const notificationsSettings = notificationsSection.querySelector('.notifications-settings');
            const deliveryMethods = notificationsSection.querySelector('.delivery-methods');

            if (notificationsContent) notificationsContent.style.marginTop = '0';
            if (notificationsGrid) notificationsGrid.style.marginTop = '20px';
            if (notificationsSettings) notificationsSettings.style.marginTop = '20px';
            if (deliveryMethods) deliveryMethods.style.marginTop = '20px';
        }
    }

    // Добавляем обработчик для переключения разделов
    document.querySelectorAll('.nav-item').forEach(button => {
        button.addEventListener('click', () => {
            // ... existing code ...
            
            // Применяем стили после переключения
            setTimeout(initializeSectionStyles, 0);
        });
    });

    // Применяем стили при первой загрузке
    document.addEventListener('DOMContentLoaded', initializeSectionStyles);
}); 