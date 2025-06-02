const langStrings = {
  "ru": {
    "my_files": "Ваши файлы",
    "trash": "Корзина",
    "welcome_dashboard": "Добро пожаловать в ваш кабинет!",
    "no_files": "Нет файлов",
    "no_trash": "Корзина пуста",
    "download": "Скачать",
    "delete": "Удалить",
    "restore": "Восстановить"
  },
  "en": {
    "my_files": "My Files",
    "trash": "Trash",
    "welcome_dashboard": "Welcome to your dashboard!",
    "no_files": "No files",
    "no_trash": "Trash is empty",
    "download": "Download",
    "delete": "Delete",
    "restore": "Restore"
  }
};

let files = [];
let trash = [];

function getLanguage() {
  return localStorage.getItem("site_lang") || "ru";
}

function setLanguage(lang) {
  document.documentElement.setAttribute("lang", lang);
  localStorage.setItem("site_lang", lang);
  updateContent(lang);

  const langSelect = document.getElementById("langSelect");
  if (langSelect) langSelect.value = lang;
}

function updateContent(lang) {
  document.querySelectorAll("[data-lang]").forEach(el => {
    const key = el.getAttribute("data-lang");
    if (langStrings[lang] && langStrings[lang][key]) {
      el.textContent = langStrings[lang][key];
    }
  });
}

function saveDataToLocalStorage() {
  localStorage.setItem("user_trash", JSON.stringify(trash));
}

async function loadFilesFromServer() {
  try {
    const response = await fetch('/api/files');
    if (!response.ok) throw new Error('Не удалось загрузить файлы');

    const data = await response.json();
    files = data;

    const savedTrash = localStorage.getItem("user_trash");
    trash = savedTrash ? JSON.parse(savedTrash) : [];

    showSection("files");
  } catch (error) {
    console.error('Ошибка при загрузке файлов:', error);
    alert('Не удалось загрузить список файлов.');
  }
}

function showSection(section) {
  const content = document.getElementById("sectionContent");
  content.innerHTML = "";

  let list = section === "files" ? files : trash;

  if (list.length === 0) {
    const p = document.createElement("p");
    p.textContent = langStrings[getCurrentLang()][section === "files" ? "no_files" : "no_trash"];
    content.appendChild(p);
    return;
  }

  // Создаем таблицу
  const table = document.createElement("table");
  table.className = "file-table";

  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  ["Имя файла", "Действия"].forEach(text => {
    const th = document.createElement("th");
    th.textContent = text;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");

  list.forEach((file, index) => {
    const row = document.createElement("tr");

    const nameCell = document.createElement("td");
    nameCell.textContent = file.name;
    row.appendChild(nameCell);

    const actionsCell = document.createElement("td");

    const downloadBtn = document.createElement("button");
    downloadBtn.textContent = langStrings[getCurrentLang()]["download"];
    downloadBtn.className = "download-btn";
    downloadBtn.onclick = () => window.open(file.path);
    actionsCell.appendChild(downloadBtn);

    if (section === "files") {
      const deleteBtn = document.createElement("button");
      deleteBtn.textContent = langStrings[getCurrentLang()]["delete"];
      deleteBtn.className = "delete-btn";
      deleteBtn.onclick = () => moveToFileTrash(index, section);
      actionsCell.appendChild(deleteBtn);
    } else if (section === "trash") {
      const restoreBtn = document.createElement("button");
      restoreBtn.textContent = langStrings[getCurrentLang()]["restore"];
      restoreBtn.className = "restore-btn";
      restoreBtn.onclick = () => restoreFromTrash(index);
      actionsCell.appendChild(restoreBtn);
    }

    row.appendChild(nameCell);
    row.appendChild(actionsCell);
    tbody.appendChild(row);
  });

  table.appendChild(tbody);
  content.appendChild(table);
}

function moveToFileTrash(index, section) {
  if (section === "files") {
    trash.push(files[index]);
    files.splice(index, 1);
  } else {
    trash.splice(index, 1);
  }

  saveDataToLocalStorage();
  showSection(section === "files" ? "files" : "trash");
}

function restoreFromTrash(index) {
  files.push(trash[index]);
  trash.splice(index, 1);
  saveDataToLocalStorage();
  showSection("trash");
}

function getCurrentLang() {
  return getLanguage();
}

window.onload = () => {
  const savedLang = getLanguage() || "ru";
  updateContent(savedLang);

  const langSelect = document.getElementById("langSelect");
  if (langSelect) {
    langSelect.value = savedLang;
    langSelect.addEventListener("change", function () {
      const selectedLang = this.value;
      setLanguage(selectedLang);
    });
  }

  loadFilesFromServer();
};