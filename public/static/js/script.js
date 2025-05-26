document.addEventListener("DOMContentLoaded", () => {
  const instituteSelect = document.getElementById("institute-select");
  const courseSelect = document.getElementById("course-select");
  const degreeSelect = document.getElementById("degree-select");
  const groupsTable = document.getElementById("groups-table");
  let selectedGroup = null;
  let currentOpenSelect = null;
  let loginEmail = "";
  let loginPassword = "";

  function initSelects() {
    instituteSelect.innerHTML = '<option value="">Выберите институт</option>';
    courseSelect.innerHTML = '<option value="">Выберите курс</option>';
    degreeSelect.innerHTML =
      '<option value="">Выберите степень обучения</option>';
    for (let i = 1; i <= 14; i++) {
      const option = document.createElement("option");
      option.value = i;
      option.textContent = `Институт №${i}`;
      instituteSelect.appendChild(option);
    }

    for (let i = 1; i <= 4; i++) {
      const option = document.createElement("option");
      option.value = i;
      option.textContent = `${i} курс`;
      courseSelect.appendChild(option);
    }

    const degrees = [
      { value: "Б", text: "Бакалавриат" },
      { value: "С", text: "Специалитет" },
      { value: "М", text: "Магистратура" },
    ];

    degrees.forEach((degree) => {
      const option = document.createElement("option");
      option.value = degree.value;
      option.textContent = degree.text;
      degreeSelect.appendChild(option);
    });
  }

  function updateGroupsTable() {
    const institute = instituteSelect.value;
    const course = courseSelect.value;
    const degree = degreeSelect.value;

    if (!institute || !course || !degree) {
      groupsTable.style.display = "none";
      return;
    }

    const currentYear = new Date().getFullYear();
    const admissionYear = String(currentYear - (parseInt(course) - 1)).slice(
      -2
    );

    let groupsHTML = '<div class="groups-table">';
    for (let i = 1; i <= 15; i++) {
      const groupNum = i < 10 ? `0${i}` : i;
      const groupCode = `M${institute}O-${course}${groupNum}${degree}-${admissionYear}`;
      groupsHTML += `<div class="group-item">${groupCode}</div>`;
    }
    groupsHTML += "</div>";

    groupsTable.innerHTML = groupsHTML;
    groupsTable.style.display = "block";

    setupGroupSelection();
  }

  function setupGroupSelection() {
    document.querySelectorAll(".group-item").forEach((item) => {
      item.addEventListener("click", function () {
        document
          .querySelectorAll(".group-item")
          .forEach((el) => el.classList.remove("selected"));
        this.classList.add("selected");
        selectedGroup = this.textContent;
        console.log("Выбрана группа:", selectedGroup);
      });
    });
  }

  function createCustomSelect(selectElement) {
    const wrapper = document.createElement("div");
    wrapper.className = "custom-select-wrapper";
    if (selectElement.classList.contains("wide-select")) {
      wrapper.classList.add("wide-select");
    }

    if (selectElement.disabled) {
      wrapper.classList.add("disabled");
    }

    const customSelect = document.createElement("div");
    customSelect.className = "custom-select";
    customSelect.textContent = selectElement.options[0].text;

    const optionsContainer = document.createElement("div");
    optionsContainer.className = "custom-options";

    Array.from(selectElement.options).forEach((option, index) => {
      const customOption = document.createElement("div");
      customOption.className = "custom-option";
      customOption.textContent = option.text;
      customOption.dataset.value = option.value;

      customOption.addEventListener("click", () => {
        selectElement.selectedIndex = index;
        customSelect.textContent = option.text;
        closeAllSelects();
        selectElement.dispatchEvent(new Event("change"));
      });

      optionsContainer.appendChild(customOption);
    });

    customSelect.addEventListener("click", (e) => {
      e.stopPropagation();
      if (selectElement.disabled) return;
      if (currentOpenSelect && currentOpenSelect !== optionsContainer) {
        currentOpenSelect.style.display = "none";
      }

      optionsContainer.style.display =
        optionsContainer.style.display === "block" ? "none" : "block";

      currentOpenSelect =
        optionsContainer.style.display === "block" ? optionsContainer : null;
    });

    wrapper.appendChild(customSelect);
    wrapper.appendChild(optionsContainer);
    selectElement.parentNode.insertBefore(wrapper, selectElement);
    selectElement.style.display = "none";
  }

  function closeAllSelects() {
    if (currentOpenSelect) {
      currentOpenSelect.style.display = "none";
      currentOpenSelect = null;
    }
  }

  initSelects();
  [instituteSelect, courseSelect, degreeSelect].forEach((select) => {
    select.addEventListener("change", updateGroupsTable);
  });
  document.querySelectorAll(".selectors-select").forEach(createCustomSelect);
  document.addEventListener("click", closeAllSelects);

  // === МОДАЛКА ПРОФИЛЯ ===
  const profileButton = document.getElementById("profile-button");
  const modal = document.getElementById("modal");

  profileButton.addEventListener("mouseenter", () =>
    modal.classList.remove("hidden")
  );
  profileButton.addEventListener("mouseleave", () => {
    setTimeout(() => {
      if (!modal.matches(":hover")) modal.classList.add("hidden");
    }, 200);
  });
  modal.addEventListener("mouseleave", () => modal.classList.add("hidden"));
  modal.addEventListener("mouseenter", () => modal.classList.remove("hidden"));

  // === ВХОД / РЕГИСТРАЦИЯ ===
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

  openLoginModalBtn1?.addEventListener("click", () =>
    loginModal.classList.remove("hidden")
  );
  openLoginModalBtn2?.addEventListener("click", () =>
    loginModal.classList.remove("hidden")
  );
  closeLoginModal?.addEventListener("click", () =>
    loginModal.classList.add("hidden")
  );

  window.addEventListener("click", (e) => {
    if (e.target === loginModal) loginModal.classList.add("hidden");
  });

  function isValidEmail(email) {
    return /^[^\s@]+@mai\.education$/.test(email.trim());
  }

  function validateInputs(showEmailError = false) {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const isAgreed = agreeCheckbox.checked;

    const isEmailValid = isValidEmail(email);
    const isPasswordFilled = password.length > 0;

    if (showEmailError) {
      emailError.style.display = isEmailValid ? "none" : "block";
    }

    agreeError.style.display = isAgreed ? "none" : "block";
    loginBtn.disabled = !(isEmailValid && isPasswordFilled && isAgreed);
  }

  emailInput.addEventListener("input", () => validateInputs(false));
  passwordInput.addEventListener("input", () => validateInputs(false));
  agreeCheckbox.addEventListener("change", () => validateInputs(false));
  emailInput.addEventListener("blur", () => validateInputs(true));

  function createLoadingOverlay() {
    const overlay = document.createElement("div");
    overlay.className = "loading-overlay";
    overlay.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(overlay);

    return {
      show: () => overlay.classList.add("visible"),
      hide: () => overlay.classList.remove("visible"),
    };
  }

  const loading = createLoadingOverlay();

  // Toast notification system
  function createToastSystem() {
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
            icon =
              '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>';
            break;
          case "error":
            icon =
              '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';
            break;
          default:
            icon =
              '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
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

  const toast = createToastSystem();

  // Enhanced form validation
  function enhanceFormValidation() {
    const emailInput = document.getElementById("emailInput");
    const passwordInput = document.getElementById("passwordInput");

    if (emailInput) {
      emailInput.addEventListener("input", () => {
        const email = emailInput.value.trim();
        if (email && !email.endsWith("@mai.education")) {
          emailInput.classList.add("invalid");
        } else {
          emailInput.classList.remove("invalid");
        }
      });
    }

    if (passwordInput) {
      passwordInput.addEventListener("input", () => {
        const password = passwordInput.value.trim();

        // Показываем ошибку только если пароль пустой
        if (password.length === 0) {
          passwordInput.classList.add("invalid");
          document.getElementById("passwordError").style.display = "block";
          document.getElementById("passwordError").textContent =
            "Введите пароль";
        } else {
          passwordInput.classList.remove("invalid");
          document.getElementById("passwordError").style.display = "none";
        }
      });
    }
  }

  loginBtn.addEventListener("click", async function () {
    loginEmail = emailInput.value.trim();
    loginPassword = passwordInput.value;
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    const agree = agreeCheckbox.checked;

    emailError.style.display = "none";
    agreeError.style.display = "none";

    if (!email.endsWith("@mai.education")) {
      emailError.style.display = "block";
      return;
    }

    if (!agree) {
      agreeError.style.display = "block";
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
        toast.show("Вход выполнен успешно!", "success");
        window.location.href = "/index2";
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
  const registerModal = document.getElementById("registerModal");
  const closeRegisterBtn = registerModal.querySelector(".close-btn");
  const registerForm = registerModal.querySelector("form");

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = loginEmail;
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
        window.location.href = "/index2";
      } else {
        alert("Ошибка регистрации: " + (data.error || "Неизвестная ошибка"));
      }
    } catch (err) {
      console.error("Ошибка регистрации:", err);
      alert("Ошибка подключения к серверу.");
    }
  });

  const registerBtn = document.getElementById("registerBtn");

  registerBtn?.addEventListener("click", () =>
    registerModal.classList.remove("hidden")
  );
  closeRegisterBtn?.addEventListener("click", () =>
    registerModal.classList.add("hidden")
  );
  window.addEventListener("click", (e) => {
    if (e.target === registerModal) registerModal.classList.add("hidden");
  });

  const logoutBtn = document.getElementById("logoutBtn");
  logoutBtn?.addEventListener(
    "click",
    () => (window.location.href = "index.html")
  );

  const profileBtn = document.getElementById("profileBtn");
  profileBtn?.addEventListener(
    "click",
    () => (window.location.href = "/index3")
  );

  const avatarBox = document.getElementById("avatarBox");
  const avatarInput = document.getElementById("avatarInput");
  const avatarPreview = document.getElementById("avatarPreview");

  avatarBox?.addEventListener("click", () => avatarInput.click());
  avatarInput?.addEventListener("change", () => {
    const file = avatarInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => (avatarPreview.src = e.target.result);
      reader.readAsDataURL(file);
    }
  });

  const editBtn = document.querySelector(".profile-edit-btn");
  const linkedSection = document.querySelector(".profile-linked-section");
  const formFields = document.querySelectorAll(
    ".profile-form-input, .profile-form-select"
  );

  if (editBtn && linkedSection) {
    formFields.forEach((el) => (el.disabled = true));

    editBtn.addEventListener("click", () => {
      const isEdit = linkedSection.classList.toggle("edit-mode");
      formFields.forEach((el) => (el.disabled = !isEdit));
      editBtn.textContent = isEdit ? "Сохранить" : "Редактирование";
    });

    linkedSection.addEventListener("click", (e) => {
      if (e.target.closest(".delete-btn")) {
        e.target.closest(".profile-linked-item").remove();
      }
    });
  }
});
document.addEventListener("DOMContentLoaded", function () {
  const openRegisterModalBtn = document.getElementById("openRegisterModalBtn");
  const registerModal = document.getElementById("registerModal");
  const closeRegisterModalBtn = registerModal.querySelector(".close-btn");

  // Открытие модального окна
  openRegisterModalBtn.addEventListener("click", function () {
    registerModal.classList.remove("hidden");
  });

  // Закрытие по кнопке "×"
  closeRegisterModalBtn.addEventListener("click", function () {
    registerModal.classList.add("hidden");
  });

  // Закрытие по клику на фон
  window.addEventListener("click", function (event) {
    if (event.target === registerModal) {
      registerModal.classList.add("hidden");
    }
  });
});
