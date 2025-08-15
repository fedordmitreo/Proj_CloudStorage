function showSection(section) {
  const sectionContent = document.getElementById("sectionContent");
  if (!sectionContent) return;
  sectionContent.innerHTML = '<p style="color: #777;">Загрузка...</p>';

  const url = section === "files" ? "/files" : "/trash";
  fetch(url)
    .then(response => response.json())
    .then(files => {
      if (section === "files") {
        renderFileList(files);
      } else {
        renderTrashList(files);
      }
    })
    .catch(err => {
      sectionContent.innerHTML = '<p style="color: #e74c3c;">Ошибка загрузки</p>';
      console.error("Fetch error:", err);
    });
}

function renderFileList(files) {
  const container = document.getElementById("sectionContent");
  container.innerHTML = "";

  if (files.length === 0) {
    container.innerHTML = "<p>Нет файлов.</p>";
    return;
  }

  files.forEach(file => {
    const el = document.createElement("div");
    el.className = "file-item";
    el.innerHTML = `
      <div class="file-name">${file}</div>
      <div class="file-actions">
        <a href="/download/${file}"><button class="restore-btn">📥 Скачать</button></a>
        <button class="delete-btn" onclick="deleteFile('${escapeHtml(file)}')">🗑 Удалить</button>
      </div>
    `;
    container.appendChild(el);
  });
}

function renderTrashList(files) {
  const container = document.getElementById("sectionContent");
  container.innerHTML = "";

  if (files.length === 0) {
    container.innerHTML = "<p>Корзина пуста.</p>";
    return;
  }

  files.forEach(file => {
    const el = document.createElement("div");
    el.className = "file-item";
    el.innerHTML = `
      <div class="file-name">${file}</div>
      <div class="file-actions">
        <button class="restore-btn" onclick="restoreFile('${escapeHtml(file)}')">🔄 Восстановить</button>
        <button class="delete-btn" onclick="deleteForever('${escapeHtml(file)}')">❌ Удалить навсегда</button>
      </div>
    `;
    container.appendChild(el);
  });
}

function deleteFile(filename) {
  fetch("/delete_file", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename })
  })
  .then(() => showSection("files"))
  .catch(() => showSection("files"));
}

function restoreFile(filename) {
  fetch("/restore_file", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename })
  })
  .then(() => showSection("trash"))
  .catch(() => showSection("trash"));
}

function deleteForever(filename) {
  fetch("/delete_permanently", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename })
  })
  .then(() => showSection("trash"))
  .catch(() => showSection("trash"));
}

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "<")
    .replace(/>/g, ">")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

document.addEventListener("DOMContentLoaded", () => {
  showSection("files");
});


const langStrings = {
  ru: {
    my_files: "Ваши файлы",
    trash: "Корзина",
    welcome_dashboard: "Добро пожаловать в ваш кабинет!",
    upload_file: "Добавить файл"
  },
  en: {
    my_files: "My Files",
    trash: "Trash",
    welcome_dashboard: "Welcome to your dashboard!",
    upload_file: "Add file"
  }
};

function setLanguage(lang) {
  document.documentElement.lang = lang;
  document.cookie = `site_lang=${lang}; path=/; max-age=31536000`;
  updateContent(lang);
  const langSelect = document.getElementById("langSelect");
  if (langSelect) langSelect.value = lang;
}

function getCookie(name) {
  const value = "; " + document.cookie;
  const parts = value.split("; " + name + "=");
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}

function updateContent(lang) {
  document.querySelectorAll("[data-lang]").forEach(el => {
    const key = el.getAttribute("data-lang");
    if (langStrings[lang] && langStrings[lang][key]) {
      el.textContent = langStrings[lang][key];
    }
  });
}

window.onload = () => {
  const savedLang = getCookie("site_lang") || "ru";
  setLanguage(savedLang);
  const langSelect = document.getElementById("langSelect");
  if (langSelect) {
    langSelect.value = savedLang;
    langSelect.addEventListener("change", () => setLanguage(langSelect.value));
  }
};