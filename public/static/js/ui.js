export function setupProfileModal() {
  const profileButton = document.getElementById("profile-button");
  const modal = document.getElementById("modal");
  const loginBtn = document.getElementById("openLoginModalBtn");
  const logoutBtn = document.getElementById("logoutBtn");
  const profileBtn = document.getElementById("profileBtn");

  function updateModalState() {
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
    if (loginBtn) loginBtn.classList.toggle('hidden', isAuthenticated);
    if (logoutBtn) logoutBtn.classList.toggle('hidden', !isAuthenticated);
    if (profileBtn) profileBtn.classList.toggle('hidden', !isAuthenticated);
  }

  // Обновляем состояние при инициализации
  updateModalState();

  // Добавляем слушатель изменений в localStorage
  window.addEventListener('storage', (e) => {
    if (e.key === 'isAuthenticated') {
      updateModalState();
    }
  });

  if (profileButton && modal) {
    profileButton.addEventListener("mouseenter", () => modal.classList.remove("hidden"));
    profileButton.addEventListener("mouseleave", () => {
      setTimeout(() => {
        if (!modal.matches(":hover")) modal.classList.add("hidden");
      }, 200);
    });
    modal.addEventListener("mouseleave", () => modal.classList.add("hidden"));
    modal.addEventListener("mouseenter", () => modal.classList.remove("hidden"));
  }

  // Кнопки для авторизованных пользователей
  document.getElementById('goToProfileBtn')?.addEventListener('click', () => {
    window.location.href = '/index3';
  });
  
  document.getElementById('goToCalendarBtn')?.addEventListener('click', () => {
    window.location.href = '/calendar';
  });
}

export function createLoadingOverlay() {
  const overlay = document.createElement("div");
  overlay.className = "loading-overlay";
  overlay.innerHTML = '<div class="spinner"></div>';
  document.body.appendChild(overlay);

  return {
    show: () => overlay.classList.add("visible"),
    hide: () => overlay.classList.remove("visible"),
  };
}

export function createToastSystem() {
  const container = document.createElement("div");
  container.className = "toast-container";
  document.body.appendChild(container);

  return {
    show: (message, type = "info", duration = 3000) => {
      const toast = document.createElement("div");
      toast.className = `toast ${type}`;

      let icon = "";
      switch (type) {
        case "success":
          icon = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>';
          break;
        case "error":
          icon = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';
          break;
        default:
          icon = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
      }

      toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
        <button class="toast-close">&times;</button>
      `;

      container.appendChild(toast);

      const closeBtn = toast.querySelector(".toast-close");
      closeBtn.addEventListener("click", () => {
        toast.classList.add("hiding");
        setTimeout(() => toast.remove(), 300);
      });

      setTimeout(() => {
        toast.classList.add("hiding");
        setTimeout(() => toast.remove(), 300);
      }, duration);
    },
  };
}