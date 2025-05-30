let currentOpenSelect = null;

export function initSelects() {
  const instituteSelect = document.getElementById("institute-select");
  const courseSelect = document.getElementById("course-select");
  const degreeSelect = document.getElementById("degree-select");
  
  if (!instituteSelect || !courseSelect || !degreeSelect) {
    return;
  }
  
  instituteSelect.innerHTML = '<option value="">Выберите институт</option>';
  courseSelect.innerHTML = '<option value="">Выберите курс</option>';
  degreeSelect.innerHTML = '<option value="">Выберите степень обучения</option>';
  
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

  document.querySelectorAll(".selectors-select").forEach(createCustomSelect);
}

export function createCustomSelect(selectElement) {
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

export function closeAllSelects() {
  if (currentOpenSelect) {
    currentOpenSelect.style.display = "none";
    currentOpenSelect = null;
  }
}

export function setupSelectListeners(updateGroupsTable) {
  const instituteSelect = document.getElementById("institute-select");
  const courseSelect = document.getElementById("course-select");
  const degreeSelect = document.getElementById("degree-select");

  if (!instituteSelect || !courseSelect || !degreeSelect) {
    return;
  }

  [instituteSelect, courseSelect, degreeSelect].forEach((select) => {
    select.addEventListener("change", updateGroupsTable);
  });
  
  document.addEventListener("click", closeAllSelects);
}