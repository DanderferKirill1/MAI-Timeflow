document.addEventListener("DOMContentLoaded", function () {
  const instituteSelect = document.getElementById("institute-select");
  const courseSelect = document.getElementById("course-select");
  const degreeSelect = document.getElementById("degree-select");
  const groupsTable = document.getElementById("groups-table");
  let selectedGroup = null;
  let currentOpenSelect = null;

  function initSelects() {
    for (let i = 1; i <= 8; i++) {
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

    document.querySelectorAll(".group-item").forEach((item) => {
      item.addEventListener("click", function () {
        document.querySelectorAll(".group-item").forEach((el) => {
          el.classList.remove("selected");
        });

        this.classList.add("selected");

        selectedGroup = this.textContent;
        console.log("Выбрана группа:", selectedGroup);
      });
    });

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

  function setupGroupItems() {
    document.querySelectorAll(".group-item").forEach((item) => {
      item.addEventListener("click", function () {
        document.querySelectorAll(".group-item").forEach((el) => {
          el.style.backgroundColor = "#ffffff";
          el.style.color = "#333";
        });

        this.style.backgroundColor = "#0095DA";
        this.style.color = "#ffffff";
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

        const event = new Event("change");
        selectElement.dispatchEvent(event);
      });

      optionsContainer.appendChild(customOption);
    });

    customSelect.addEventListener("click", (e) => {
      e.stopPropagation();

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

  document.addEventListener("click", closeAllSelects);

  document.querySelectorAll(".selectors select").forEach((select) => {
    createCustomSelect(select);
  });

  function init() {
    initSelects();
    [instituteSelect, courseSelect, degreeSelect].forEach((select) => {
      select.addEventListener("change", updateGroupsTable);
    });
  }

  init();
});

const profileButton = document.getElementById("profile-button");
const modal = document.getElementById("modal");

profileButton.addEventListener("mouseenter", () => {
  modal.classList.remove("hidden");
});

profileButton.addEventListener("mouseleave", () => {
  setTimeout(() => {
    if (!modal.matches(":hover")) {
      modal.classList.add("hidden");
    }
  }, 200);
});

modal.addEventListener("mouseleave", () => {
  modal.classList.add("hidden");
});

modal.addEventListener("mouseenter", () => {
  modal.classList.remove("hidden");
});

document.addEventListener("DOMContentLoaded", () => {
  const openLoginModalBtn = document.getElementById("openLoginModalBtn");
  const loginModal = document.getElementById("loginModal");
  const closeLoginModal = document.getElementById("closeLoginModal");

  openLoginModalBtn.addEventListener("click", () => {
    loginModal.classList.remove("hidden");
  });

  closeLoginModal.addEventListener("click", () => {
    loginModal.classList.add("hidden");
  });

  const emailInput = document.getElementById("emailInput");
  const emailError = document.getElementById("emailError");
  const passwordInput = document.getElementById("passwordInput");
  const loginBtn = document.getElementById("loginBtn");
  const agreeCheckbox = document.getElementById("agreeCheckbox");
  const agreeError = document.getElementById("agreeError");

  function isValidEmail(email) {
    const maiRegex = /^[^\s@]+@mai\.education$/i;
    return maiRegex.test(email.trim());
  }

  function validateInputs(showEmailError = false) {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const isAgreed = agreeCheckbox.checked;

    const isEmailValid = isValidEmail(email);
    const isPasswordFilled = password.length > 0;

    // Показываем email ошибку только если явно просим (при blur)
    if (showEmailError) {
      emailError.style.display = isEmailValid ? "none" : "block";
    }

    // Согласие — можно сразу проверять
    agreeError.style.display = isAgreed ? "none" : "block";

    // Кнопка активна, если всё корректно
    loginBtn.disabled = !(isEmailValid && isPasswordFilled && isAgreed);
  }

  // Проверка при вводе
  emailInput.addEventListener("input", () => validateInputs(false));
  passwordInput.addEventListener("input", () => validateInputs(false));
  agreeCheckbox.addEventListener("change", () => validateInputs(false));

  // Показываем ошибку email только при уходе с поля
  emailInput.addEventListener("blur", () => validateInputs(true));

  loginBtn.addEventListener("click", () => {
    if (loginBtn.disabled) return;

    window.location.href = "index2.html";
  });
});
document.addEventListener("DOMContentLoaded", () => {
  const registerBtn = document.getElementById("registerBtn");
  const registerModal = document.getElementById("registerModal");
  const closeBtn = registerModal.querySelector(".close-btn");

  // Открытие модалки
  registerBtn.addEventListener("click", () => {
    registerModal.classList.remove("hidden");
  });

  // Закрытие при нажатии на крестик
  closeBtn.addEventListener("click", () => {
    registerModal.classList.add("hidden");
  });

  // Закрытие при клике вне окна
  window.addEventListener("click", (e) => {
    if (e.target === registerModal) {
      registerModal.classList.add("hidden");
    }
  });
});
