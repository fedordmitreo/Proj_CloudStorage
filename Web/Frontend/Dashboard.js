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

// Получаем язык
function getLanguage() {
  return localStorage.getItem("site_lang") || "ru";
}

// Сохраняем язык
function setLanguage(lang) {
  document.documentElement.setAttribute("lang", lang);
  localStorage.setItem("site_lang", lang);
  updateContent(lang);

  const langSelect = document.getElementById("langSelect");
  if (langSelect) langSelect.value = lang;
}

// Обновляем текст на странице
function updateContent(lang) {
  document.querySelectorAll("[data-lang]").forEach(el => {
    const key = el.getAttribute("data-lang");
    if (langStrings[lang] && langStrings[lang][key]) {
      el.textContent = langStrings[lang][key];
    }
  });
}

// Сохраняем данные в localStorage
function saveDataToLocalStorage() {
  localStorage.setItem("user_trash", JSON.stringify(trash));
}

// Загружаем список файлов с помощью fetch
async function loadFilesFromServer() {
  try {
    const response = await fetch('/api/files');
    if (!response.ok) throw new Error('Не удалось загрузить файлы');

    const data = await response.json();
    files = data;

    // Проверяем корзину
    const savedTrash = localStorage.getItem("user_trash");
    trash = savedTrash ? JSON.parse(savedTrash) : [];

    showSection("files");
  } catch (error) {
    console.error('Ошибка при загрузке файлов:', error);
    alert('Не удалось загрузить список файлов.');
  }
}

// Отображение раздела: "Ваши файлы" или "Корзина"
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

  const ul = document.createElement("div");
  ul.className = "file-list";

  list.forEach((file, index) => {
    const li = document.createElement("div");
    li.className = "file-item";

    const span = document.createElement("span");
    span.className = "file-name";
    span.textContent = file.name;

    const actions = document.createElement("div");
    actions.className = "file-actions";

    const downloadBtn = document.createElement("button");
    downloadBtn.textContent = langStrings[getCurrentLang()]["download"];
    downloadBtn.onclick = () => window.open(file.path);

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = langStrings[getCurrentLang()]["delete"];
    deleteBtn.className = "delete-btn";
    deleteBtn.onclick = () => moveToFileTrash(index, section);

    if (section === "trash") {
      const restoreBtn = document.createElement("button");
      restoreBtn.textContent = langStrings[getCurrentLang()]["restore"];
      restoreBtn.className = "restore-btn";
      restoreBtn.onclick = () => restoreFromTrash(index);
      actions.appendChild(restoreBtn);
    }

    actions.appendChild(downloadBtn);
    actions.appendChild(deleteBtn);

    li.appendChild(span);
    li.appendChild(actions);

    ul.appendChild(li);
  });

  content.appendChild(ul);
}

// Перемещение файла в корзину
function moveToFileTrash(index, section) {
  if (section === "files") {
    trash.push(files[index]);
    files.splice(index, 1);
  } else {
    trash.splice(index, 1);
  }

  saveDataToLocalStorage(); // Сохраняем в localStorage
  showSection(section === "files" ? "files" : "trash");
}

// Восстановление из корзины
function restoreFromTrash(index) {
  files.push(trash[index]);
  trash.splice(index, 1);

  saveDataToLocalStorage(); // Сохраняем в localStorage
  showSection("files");
}

// Получаем текущий язык
function getCurrentLang() {
  return getLanguage();
}

window.onload = () => {
  const savedLang = getLanguage() || "ru";
  updateContent(savedLang);

  const langSelect = document.getElementById("langSelect");
  if (langSelect) langSelect.value = savedLang;

  langSelect.addEventListener("change", function () {
    const selectedLang = this.value;
    setLanguage(selectedLang);
  });

  loadFilesFromServer(); // Загружаем файлы
};