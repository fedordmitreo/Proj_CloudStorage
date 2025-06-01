const langStrings = {
    "ru": {
        "my_files": "Ваши файлы",
        "trash": "Корзина",
        "welcome_dashboard": "Добро пожаловать в ваш кабинет!"
    },
    "en": {
        "my_files": "My Files",
        "trash": "Trash",
        "welcome_dashboard": "Welcome to your dashboard!"
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