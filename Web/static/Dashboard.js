function showSection(section) {
  const sectionContent = document.getElementById("sectionContent");
  sectionContent.innerHTML = "Loading...";

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
              <button class="restore-btn" onclick="restoreFile('${file}')">Restore</button>
              <button class="delete-btn" onclick="deleteForever('${file}')">Delete permanently</button>
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
          <button class="restore-btn">📥 Download</button>
        </a>
        <button class="delete-btn" onclick="deleteFile('${file}')">🗑 Delete</button>
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

const langStrings = {

    "ru": {
        "my_files": "Ваши файлы",
        "trash": "Корзина",
        "welcome_dashboard": "Добро пожаловать в ваш кабинет!",
        "upload_file": "Добавить файл"
    },
    "en": {
        "my_files": "My Files",
        "trash": "Trash",
        "welcome_dashboard": "Welcome to your dashboard!",
        "upload_file": "Add file"
    }
};

function setLanguage(lang) {
    document.documentElement.setAttribute("lang", lang);
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
    const savedLang = getCookie("site_lang") || "en";
    updateContent(savedLang);
    const langSelect = document.getElementById("langSelect");

    if (langSelect) langSelect.value = savedLang;
    langSelect.addEventListener("change", function () {
        const selectedLang = this.value;
        setLanguage(selectedLang);
    });
};