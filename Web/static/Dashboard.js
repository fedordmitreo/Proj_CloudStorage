function showSection(section) {
  const sectionContent = document.getElementById("sectionContent");
  sectionContent.innerHTML = "Загрузка...";

  if (section === "files") {
    fetch("/files")
      .then(response => response.json())
      .then(files => {
        renderFileList(files);
      });
  } else if (section === "trash") {
    fetch("/trash")
      .then(response => response.json())
      .then(files => {
        sectionContent.innerHTML = files.map(file => `
          <div class="file-item">
            <span class="file-name">${file}</span>
            <div class="file-actions">
              <button class="restore-btn" onclick="restoreFile('${file}')">Восстановить</button>
              <button class="delete-btn" onclick="deleteForever('${file}')">Удалить навсегда</button>
            </div>
          </div>
        `).join("");
      });
  }
}

function renderFileList(files) {
  const container = document.getElementById("sectionContent");
  container.innerHTML = "";

  files.forEach(file => {
    const fileDiv = document.createElement("div");
    fileDiv.className = "file-item";

    fileDiv.innerHTML = `
      <div class="file-name">${file}</div>
      <div class="file-actions">
        <a href="/download/${file}">
          <button class="restore-btn">📥 Скачать</button>
        </a>
        <button class="delete-btn" onclick="deleteFile('${file}')">🗑 Удалить</button>
      </div>
    `;

    container.appendChild(fileDiv);
  });
}

function deleteFile(filename) {
  fetch("/delete_file", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename })
  }).then(() => showSection("files"));
}

function restoreFile(filename) {
  fetch("/restore_file", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename })
  }).then(() => showSection("trash"));
}

function deleteForever(filename) {
  fetch("/delete_permanently", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename })
  }).then(() => showSection("trash"));
}

// При загрузке страницы сразу показываем файлы
document.addEventListener("DOMContentLoaded", () => {
  showSection("files");
});
