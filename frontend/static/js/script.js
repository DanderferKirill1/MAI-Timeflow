fetch("/api/data", {
    headers: { "Content-Type": "application/json" }
  })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error("Ошибка:", error));