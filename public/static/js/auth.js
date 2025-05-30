// auth.js

// Получение текущего статуса авторизации
export function getAuthStatus() {
  return localStorage.getItem('access_token') !== null;
}

// Переключение видимости элементов в зависимости от статуса авторизации
export function toggleAuthState() {
  const isAuthenticated = getAuthStatus();

  const authElements = document.querySelectorAll('.auth-only');
  const unauthElements = document.querySelectorAll('.unauth-only');

  authElements.forEach(el => {
    if (el.classList.contains('hidden')) {
      el.classList.remove('hidden');
    }
    el.style.display = isAuthenticated ? 'block' : 'none';
  });
  
  unauthElements.forEach(el => {
    el.style.display = isAuthenticated ? 'none' : 'block';
  });

  // Обновляем видимость кнопок "Начать" и "Профиль"
  const startButton = document.getElementById('openLoginModalBtn2');
  const profileButton = document.getElementById('goToProfileBtn');
  
  if (startButton) {
    startButton.style.display = isAuthenticated ? 'none' : 'block';
  }
  if (profileButton) {
    profileButton.style.display = isAuthenticated ? 'block' : 'none';
  }

  // Обновляем видимость блока преимуществ
  const advantagesBlock = document.querySelector('.advantages-block');
  if (advantagesBlock) {
    advantagesBlock.style.display = isAuthenticated ? 'none' : 'block';
  }
}

// Функция для выхода из системы
export function handleLogout() {
  localStorage.removeItem("access_token");
  localStorage.setItem("isAuthenticated", "false");
  // Вызываем событие storage вручную
  window.dispatchEvent(new StorageEvent('storage', {
    key: 'isAuthenticated',
    newValue: 'false'
  }));
  toggleAuthState();
  // Используем window.toast если он доступен
  if (window.toast) {
    window.toast.show("Вы успешно вышли из системы", "success");
  }
  // Переадресация на главную страницу
  window.location.href = '/';
}

// Установка обработчиков для логина, регистрации и выхода
export function setupAuthHandlers(toast, loading) {
  // Сохраняем toast в глобальной области видимости
  window.toast = toast;

  const loginModal = document.getElementById("loginModal");
  const openLoginModalBtn1 = document.getElementById("openLoginModalBtn");
  const openLoginModalBtn2 = document.getElementById("openLoginModalBtn2");
  const closeLoginModal = document.getElementById("closeLoginModal");
  const emailInput = document.getElementById("emailInput");
  const passwordInput = document.getElementById("passwordInput");
  const loginBtn = document.getElementById("loginBtn");
  const agreeCheckbox = document.getElementById("agreeCheckbox");
  const emailError = document.getElementById("emailError");
  const agreeError = document.getElementById("agreeError");
  const passwordError = document.createElement('small');
  passwordError.style.color = 'red';
  passwordError.style.display = 'none';
  passwordError.id = 'passwordError';
  passwordInput.parentNode.insertBefore(passwordError, passwordInput.nextSibling);

  let loginEmail = "";
  let loginPassword = "";

  // Открытие/закрытие модального окна входа
  openLoginModalBtn1?.addEventListener("click", () => loginModal.classList.remove("hidden"));
  openLoginModalBtn2?.addEventListener("click", () => loginModal.classList.remove("hidden"));
  closeLoginModal?.addEventListener("click", () => loginModal.classList.add("hidden"));
  window.addEventListener("click", e => {
    if (e.target === loginModal) loginModal.classList.add("hidden");
  });

  // Валидация email (только @mai.education)
  function isValidEmail(email) {
    return /^[^\s@]+@mai\.education$/.test(email.trim());
  }

  // Валидация пароля
  function validatePassword(password) {
    if (password.length === 0) {
      passwordError.style.display = 'none';
      return false;
    }
    if (password.length < 8) {
      passwordError.textContent = 'Пароль должен содержать минимум 8 символов';
      passwordError.style.display = 'block';
      return false;
    }
    passwordError.style.display = 'none';
    return true;
  }

  // Проверка всех входных данных для активации кнопки входа
  function validateInputs(showEmailError = false) {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const isAgreed = agreeCheckbox.checked;

    const isEmailValid = isValidEmail(email);
    const isPasswordValid = password.length === 0 || validatePassword(password);

    if (showEmailError) {
      emailError.style.display = isEmailValid ? "none" : "block";
    }

    agreeError.style.display = isAgreed ? "none" : "block";
    loginBtn.disabled = !(isEmailValid && (password.length === 0 || isPasswordValid) && isAgreed);
  }

  emailInput?.addEventListener("input", () => validateInputs(false));
  passwordInput?.addEventListener("input", () => validateInputs(false));
  agreeCheckbox?.addEventListener("change", () => validateInputs(false));
  emailInput?.addEventListener("blur", () => validateInputs(true));

  // Обработчик кнопки входа
  loginBtn?.addEventListener("click", async () => {
    loginEmail = emailInput.value.trim();
    loginPassword = passwordInput.value;
    const email = loginEmail;
    const password = loginPassword;
    const agree = agreeCheckbox.checked;

    emailError.style.display = "none";
    agreeError.style.display = "none";
    loading.show();

    if (!email.endsWith("@mai.education")) {
      emailError.style.display = "block";
      loading.hide();
      return;
    }
    if (!agree) {
      agreeError.style.display = "block";
      loading.hide();
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        const message = data?.message || "Неверная почта или пароль";
        toast.show(message, "error");
        return;
      }

      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("isAuthenticated", "true");
        // Вызываем событие storage вручную
        window.dispatchEvent(new StorageEvent('storage', {
          key: 'isAuthenticated',
          newValue: 'true'
        }));
        toggleAuthState();
        toast.show("Вход выполнен успешно!", "success");
        loginModal.classList.add("hidden");
        return;
      }

      if (data.status === "register") {
        loginModal.classList.add("hidden");
        document.getElementById("firstName").focus();
        document.getElementById("registerModal").classList.remove("hidden");
        toast.show("Пожалуйста, заполните данные для регистрации", "info");
        return;
      }

      toast.show("Неверная почта или пароль", "error");
    } catch (error) {
      console.error("Login error:", error);
      toast.show("Ошибка соединения с сервером", "error");
    } finally {
      loading.hide();
    }
  });

  // Регистрация пользователя
  const registerModal = document.getElementById("registerModal");
  const closeRegisterBtn = registerModal?.querySelector(".close-btn");
  const registerForm = registerModal?.querySelector("form");
  const openRegisterModalBtn = document.getElementById("openRegisterModalBtn");

  registerForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    loading.show();

    const firstName = document.getElementById("firstName").value.trim();
    const lastName = document.getElementById("lastName").value.trim();
    const group = document.getElementById("group").value.trim();

    try {
      const response = await fetch("http://127.0.0.1:5000/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: loginEmail,
          password: loginPassword,
          first_name: firstName,
          last_name: lastName,
          group_code: group,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("isAuthenticated", "true");
        toggleAuthState();
        registerModal.classList.add("hidden");
        toast.show("Регистрация прошла успешно!", "success");
      } else {
        toast.show("Ошибка регистрации: " + (data.error || "Неизвестная ошибка"), "error");
      }
    } catch (err) {
      console.error("Ошибка регистрации:", err);
      toast.show("Ошибка подключения к серверу.", "error");
    } finally {
      loading.hide();
    }
  });

  openRegisterModalBtn?.addEventListener("click", () => registerModal.classList.remove("hidden"));
  closeRegisterBtn?.addEventListener("click", () => registerModal.classList.add("hidden"));
  window.addEventListener("click", (e) => {
    if (e.target === registerModal) registerModal.classList.add("hidden");
  });

  // Выход из системы
  document.getElementById("logoutBtn")?.addEventListener("click", async () => {
    try {
      const token = localStorage.getItem("access_token");
      
      // Если токен отсутствует или истек, просто очищаем локальное хранилище
      if (!token) {
        handleLogout();
        return;
      }

      const response = await fetch("http://127.0.0.1:5000/api/logout", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });

      if (!response.ok) {
        // Если токен истек или другая ошибка авторизации, просто очищаем хранилище
        if (response.status === 401 || response.status === 422) {
          handleLogout();
          return;
        }
        throw new Error('Ошибка при выходе из системы');
      }

      handleLogout();
      
    } catch (error) {
      console.error("Ошибка при выходе:", error);
      // В случае любой ошибки, все равно разлогиниваем пользователя
      handleLogout();
    }
  });
}

async function checkToken() {
  const token = localStorage.getItem('access_token');
  if (!token) return false;

  try {
    const response = await fetch('http://127.0.0.1:5000/api/check-token', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Токен истек или недействителен
        handleLogout();
        return false;
      }
      throw new Error('Ошибка проверки токена');
    }

    return true;
  } catch (error) {
    console.error('Ошибка при проверке токена:', error);
    handleLogout();
    return false;
  }
}

// Добавляем проверку токена при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
  if (localStorage.getItem('access_token')) {
    const isValid = await checkToken();
    if (!isValid) {
      handleLogout();
    } else {
    toggleAuthState();
    }
  }
});

// Модифицируем функцию выхода
export async function logout() {
  try {
    const token = localStorage.getItem('access_token');
    if (token) {
      await fetch('/api/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    }
  } catch (error) {
    console.error('Ошибка при выходе:', error);
  } finally {
    handleLogout();
    window.location.href = '/';
  }
}
