
async function generate() {
  const statusEl = document.getElementById("status");
  const docLink = document.getElementById("doc-link");
  const pptLink = document.getElementById("ppt-link");

  // Показываем сообщение о загрузке
  statusEl.textContent = "Идет генерация, это может занять некоторое время...";
  docLink.style.display = "none";
  pptLink.style.display = "none";

  const topic = document.getElementById("topic").value;
  try {
    const response = await fetch("/generate", {
      method: "POST",
      body: new URLSearchParams({ topic }),
    });
    const data = await response.json();

    if (data.message === "Успешно") {
      statusEl.textContent = "Генерация завершена! Скачайте файлы ниже.";
      docLink.href = data.doc;
      pptLink.href = data.ppt;
      docLink.textContent = "Скачать DOCX";
      pptLink.textContent = "Скачать PPTX";
      docLink.style.display = "inline";
      pptLink.style.display = "inline";
    } else {
      statusEl.textContent = "";
      alert(data.message);
    }
  } catch (e) {
    statusEl.textContent = "";
    alert("Ошибка при соединении с сервером.");
  }
}

