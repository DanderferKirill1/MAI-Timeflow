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

const levelMap = {
  "Б": "Бакалавриат",
  "С": "Специалитет",
  "М": "Магистратура"
};

let selectedGroup = null;

function initGroupsHandler() {
  const instituteSelect = document.getElementById("institute-select");
  const courseSelect = document.getElementById("course-select");
  const degreeSelect = document.getElementById("degree-select");
  
  // Если мы не на странице с селектами, просто выходим
  if (!instituteSelect || !courseSelect || !degreeSelect) {
    return;
  }

  [instituteSelect, courseSelect, degreeSelect].forEach(select => {
    select.addEventListener('change', handleSelectChange);
  });
}

async function handleSelectChange() {
  const instituteSelect = document.getElementById("institute-select");
  const courseSelect = document.getElementById("course-select");
  const degreeSelect = document.getElementById("degree-select");
  
  const institute = instituteSelect.value;
  const course = courseSelect.value;
  const degree = degreeSelect.value;

  if (!institute || !course || !degree) {
    clearGroups();
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:5000/api/schedule_groups", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        institute_name: instituteMap[institute],
        course_number: course,
        level_name: levelMap[degree]
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Ошибка при получении групп');
    }

    const data = await response.json();
    console.log('Получены группы:', data);
    
    if (data.groups && Array.isArray(data.groups)) {
      displayGroups(data.groups);
    } else {
      console.error('Неверный формат данных:', data);
      clearGroups();
    }
  } catch (error) {
    console.error('Ошибка:', error);
    clearGroups();
  }
}

function clearGroups() {
  const container = document.getElementById('groups-table');
  const label = document.getElementById('groups-table-label');
  if (container) {
    container.innerHTML = '';
    container.classList.remove('visible');
    container.classList.add('hidden');
    if (label) label.style.display = '';
  }
}

function displayGroups(groups) {
  const container = document.getElementById('groups-table');
  if (!container) {
    console.error('Контейнер для групп не найден');
    return;
  }

  // Очищаем контейнер
  container.innerHTML = '';

  // Создаём label всегда
  const label = document.createElement('div');
  label.id = 'groups-table-label';
  label.className = 'groups-table-label';
  label.textContent = 'Выберите вашу группу:';
  container.appendChild(label);

  if (!groups || groups.length === 0) {
    container.innerHTML += '<p class="error">Нет доступных групп</p>';
    container.classList.add('visible');
    return;
  }

  // Создаем сетку для групп
  const grid = document.createElement('div');
  grid.className = 'groups-table';

  groups.forEach(group => {
    const groupItem = document.createElement('div');
    groupItem.className = 'group-item';
    groupItem.textContent = group;

    groupItem.addEventListener('click', () => {
      // Убираем выделение с предыдущей группы
      const previousSelected = container.querySelector('.group-item.selected');
      if (previousSelected) {
        previousSelected.classList.remove('selected');
      }

      // Выделяем текущую группу
      groupItem.classList.add('selected');
      selectedGroup = group;
      // Вызываем событие выбора группы
      const event = new CustomEvent('groupSelected', { detail: group });
      document.dispatchEvent(event);
    });

    grid.appendChild(groupItem);
  });

  container.appendChild(grid);
  container.classList.remove('hidden');
  container.classList.add('visible');

  // Рассчитываем количество строк
  const containerWidth = 880; // Ширина контейнера
  const itemWidth = 200; // Минимальная ширина элемента
  const gap = 15; // Отступ между элементами
  const itemsPerRow = Math.floor((containerWidth + gap) / (itemWidth + gap));
  const rows = Math.ceil(groups.length / itemsPerRow);

  // Рассчитываем высоту
  const itemHeight = 45; // Высота элемента
  const headerHeight = 30; // Высота заголовка
  const verticalPadding = 60; // Общий вертикальный padding (45px сверху + 15px снизу)
  const verticalGap = 15; // Вертикальный отступ между строками

  const totalHeight = headerHeight + verticalPadding + (itemHeight * rows) + (verticalGap * (rows - 1));
  container.style.height = `${totalHeight}px`;
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', initGroupsHandler);

export { selectedGroup, initGroupsHandler }; 