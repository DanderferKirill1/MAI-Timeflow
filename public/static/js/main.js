// main.js
import { getAuthStatus, toggleAuthState, setupAuthHandlers } from './auth.js';
import { initSelects, createCustomSelect, closeAllSelects, setupSelectListeners } from './selects.js';
import { initGroupsHandler } from './groups-handler.js';
import { setupProfileModal, createLoadingOverlay, createToastSystem } from './ui.js';

document.addEventListener("DOMContentLoaded", () => {
  const toast = createToastSystem();
  const loading = createLoadingOverlay();

  function initPage() {
    initSelects();
    toggleAuthState();
    setupEventListeners();
    initGroupsHandler();
  }

  function setupEventListeners() {
    // Проверяем, находимся ли мы на странице с селектами
    const instituteSelect = document.getElementById("institute-select");
    if (instituteSelect) {
      setupSelectListeners(() => {
        // Пустая функция, так как обработчик групп уже установлен в initGroupsHandler
      });
    }
    setupProfileModal();
    setupAuthHandlers(toast, loading);
    document.addEventListener("click", closeAllSelects);
  }

  // Динамическое состояние авторизации — всегда свежий статус из localStorage
  Object.defineProperty(window, "appState", {
    configurable: true,
    enumerable: true,
    get() {
      return {
        get isAuthenticated() {
          return getAuthStatus();
        }
      };
    }
  });

  initPage();
});
