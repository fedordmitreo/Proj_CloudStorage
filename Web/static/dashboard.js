function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "<")
    .replace(/>/g, ">")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

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
    container.innerHTML = "<p data-lang='nof'>Нет файлов.</p>";
    return;
  }

  files.forEach(file => {
    const el = document.createElement("div");
    el.className = "file-item";
    el.innerHTML = `
      <div class="file-name">${escapeHtml(file)}</div>
      <div class="file-actions">
        <a href="/download/${encodeURIComponent(file)}"><button data-lang="download" class="restore-btn">📥 Скачать</button></a>
        <button class="delete-btn" data-lang="del" onclick="deleteFile('${escapeHtml(file)}')">🗑 Удалить</button>
      </div>
    `;
    container.appendChild(el);
  });
}

function renderTrashList(files) {
  const container = document.getElementById("sectionContent");
  container.innerHTML = "";

  if (files.length === 0) {
    container.innerHTML = "<p data-lang='nof'>Корзина пуста.</p>";
    return;
  }

  files.forEach(file => {
    const el = document.createElement("div");
    el.className = "file-item";
    el.innerHTML = `
      <div class="file-name">${escapeHtml(file)}</div>
      <div class="file-actions">
        <button class="restore-btn" data-lang="vost" onclick="restoreFile('${escapeHtml(file)}')">🔄 Восстановить</button>
        <button class="delete-btn" data-lang="del" onclick="deleteForever('${escapeHtml(file)}')">❌ Удалить навсегда</button>
      </div>
    `;
    container.appendChild(el);
  });
}

// Удаление файла в корзину
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

const langStrings = {
  ru: {
    my_files: "Ваши файлы",
    trash: "Корзина",
    welcome_dashboard: "Добро пожаловать в ваш кабинет!",
    upload_file: "Добавить файл",
    vost: "🔄 Восстановить",
    del: "❌ Удалить",
    download: "📥 Скачать",
    nof: "Нет файлов"
  },
  en: {
    my_files: "My Files",
    trash: "Trash",
    welcome_dashboard: "Welcome to your dashboard!",
    upload_file: "Add file",
    vost: "🔄 Restore",
    del: "❌ Delete",
    download: "📥 Download",
    nof: "No files"
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

document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("uploadForm");
  if (uploadForm) {
    uploadForm.addEventListener("submit", function(e) {
      e.preventDefault();
      
      const fileInput = document.getElementById("fileInput");
      const file = fileInput.files[0];
      if (!file) {
        alert("Пожалуйста, выберите файл");
        return;
      }

      const formData = new FormData();
      formData.append("file", file);

      const progressContainer = document.querySelector(".progress-container");
      const progressFill = document.querySelector(".progress-fill");
      const progressText = document.querySelector(".progress-text");

      progressContainer.style.display = "block";
      progressFill.style.width = "0%";
      progressText.textContent = "0%";

      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener("progress", function(e) {
        if (e.lengthComputable) {
          const percent = Math.round((e.loaded / e.total) * 100);
          progressFill.style.width = percent + "%";
          progressText.textContent = percent + "%";
        }
      });

      xhr.addEventListener("load", function() {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          if (response.success) {
            fileInput.value = "";
            progressContainer.style.display = "none";
            showSection("files");
          } else {
            alert("Ошибка: " + (response.message || "Неизвестная ошибка"));
            progressContainer.style.display = "none";
          }
        } else {
          alert("Ошибка сервера: " + xhr.status);
          progressContainer.style.display = "none";
        }
      });

      xhr.addEventListener("error", function() {
        alert("Ошибка сети");
        progressContainer.style.display = "none";
      });

      xhr.open("POST", "/upload");
      xhr.send(formData);
    });
  }

  const savedLang = getCookie("site_lang") || "ru";
  setLanguage(savedLang);
  const langSelect = document.getElementById("langSelect");
  if (langSelect) {
    langSelect.value = savedLang;
    langSelect.addEventListener("change", () => setLanguage(langSelect.value));
  }
  showSection("files");
});
