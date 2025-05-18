document.addEventListener("DOMContentLoaded", () => {
  const showBtn = document.querySelector(".show-timetable");
  const wrapper = document.getElementById("timetable-wrapper");
  const timetable = document.getElementById("timetable");

  const scheduleData = [
    { date: "12.05", day: "Понедельник", lessons: [] },
    { date: "13.05", day: "Вторник", lessons: [] },
    {
      date: "14.05",
      day: "Среда",
      lessons: [
        "9:00 – 10:30 Математическое моделирование ГУК Б 216",
        "10:45 – 12:15 Физика 5 216",
        "13:00 – 14:30 Математическое моделирование ГУК Б 216",
        "14:45 – 16:15 Математическое моделирование ГУК Б 216",
        "16:30 – 18:00 Математическое моделирование ГУК Б 216",
      ],
    },
    {
      date: "15.05",
      day: "Четверг",
      lessons: [
        "9:00 – 10:30 Математическое моделирование ГУК Б 216",
        "10:45 – 12:15 Физика 5 216",
        "13:00 – 14:30 Математическое моделирование ГУК Б 216",
        "14:45 – 16:15 Математическое моделирование ГУК Б 216",
        "16:30 – 18:00 Математическое моделирование ГУК Б 216",
      ],
    },
    { date: "16.05", day: "Пятница", lessons: [] },
    { date: "17.05", day: "Суббота", lessons: [] },
    {
      date: "18.05",
      day: "Воскресенье",
      lessons: [
        "9:00 – 10:30 Математическое моделирование ГУК Б 216",
        "10:45 – 12:15 Физика 5 216",
        "13:00 – 14:30 Математическое моделирование ГУК Б 216",
        "14:45 – 16:15 Математическое моделирование ГУК Б 216",
        "16:30 – 18:00 Математическое моделирование ГУК Б 216",
      ],
    },
  ];

  if (!showBtn || !wrapper || !timetable) {
    console.error(
      "❌ Один из элементов не найден: showBtn, wrapper или timetable"
    );
    return;
  }

  showBtn.addEventListener("click", () => {
    wrapper.classList.remove("hidden");
    timetable.innerHTML = "";

    scheduleData.forEach((day) => {
      const dayDiv = document.createElement("div");
      dayDiv.className = "day-card";

      const title = document.createElement("h3");
      title.innerHTML = `<small>${day.date}</small><br>${day.day}`;
      dayDiv.appendChild(title);

      if (day.lessons.length === 0) {
        const p = document.createElement("p");
        p.className = "lesson";
        p.textContent = "Занятий нет";
        dayDiv.appendChild(p);
      } else {
        day.lessons.forEach((lesson) => {
          const p = document.createElement("p");
          p.className = "lesson";
          p.textContent = lesson;
          dayDiv.appendChild(p);
        });
      }

      timetable.appendChild(dayDiv);
    });
  });
});
