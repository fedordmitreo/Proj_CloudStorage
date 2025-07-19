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

// Инициализация файлов и корзины из localStorage или по умолчанию
let files = [];
let trash = [];

const savedFiles = localStorage.getItem("user_files");
const savedTrash = localStorage.getItem("user_trash");

if (savedFiles) {
  files = JSON.parse(savedFiles);
} else {
  files = [
    { name: "document1.pdf", path: "files/document1.pdf" },
    { name: "image1.jpg", path: "files/image1.jpg" },
    { name: "example.txt", path: "files/example.txt" }
  ];
}

if (savedTrash) {
  trash = JSON.parse(savedTrash);
} else {
  trash = [];
}

// Функция для сохранения файлов и корзины в localStorage
function saveDataToLocalStorage() {
  localStorage.setItem("user_files", JSON.stringify(files));
  localStorage.setItem("user_trash", JSON.stringify(trash));
}

// Смена языка
function setLanguage(lang) {
  document.documentElement.setAttribute("lang", lang);
  localStorage.setItem("site_lang", lang);
  updateContent(lang);

  const langSelect = document.getElementById("langSelect");
  if (langSelect) langSelect.value = lang;
}

function getLanguage() {
  return localStorage.getItem("site_lang") || "ru";
}

function updateContent(lang) {
  document.querySelectorAll("[data-lang]").forEach(el => {
    const key = el.getAttribute("data-lang");
    if (langStrings[lang] && langStrings[lang][key]) {
      el.textContent = langStrings[lang][key];
    }
  });
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

function restoreFromTrash(index) {
  files.push(trash[index]);
  trash.splice(index, 1);

  saveDataToLocalStorage(); // Сохраняем в localStorage
  showSection("files");
}

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

  showSection("files");
};