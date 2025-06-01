const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.querySelector('.container');

signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});


document.getElementById('signup').addEventListener('submit', function (e) {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    setCookie('userName', name, 2);
    setCookie('userEmail', email, 2);
    setCookie('userPassword', password, 2);
    alert('Данные сохранены в cookie!');
});

function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + encodeURIComponent(value) + expires + "; path=/";
}

function getCookie(name) {
    const nameEQ = name + "=";
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return null;
}

window.addEventListener('load', function () {
    const savedName = getCookie('userName');
    const savedEmail = getCookie('userEmail');

    if (savedName) {
        document.getElementById('name').value = savedName;
    }

    if (savedEmail) {
        document.getElementById('email').value = savedEmail;
    }

});

// Устанавливаем язык и сохраняем его в cookie
function setLanguage(lang) {
    // Сохраняем в cookie на 30 дней
    setCookie("site_lang", lang, 30);
    
    // Обновляем текст на странице
    updateContent(lang);
}

// Функция обновления текста на странице
function updateContent(lang) {
    document.querySelectorAll("[data-lang]").forEach(el => {
        const key = el.getAttribute("data-lang");
        el.textContent = langStrings[lang][key] || el.textContent;
    });
}

// Функция для работы с cookie
function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + encodeURIComponent(value) + expires + "; path=/";
}

function getCookie(name) {
    const nameEQ = name + "=";
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return null;
}

// Словарь переводов
const langStrings = {
    "ru": {
        "welcome": "Добро пожаловать!",
        "description-singup": "Введите свои данные и зарегистрируйтесь",
        "description-singin": "Введите свои данные для входа в систему",
        "signin": "Войти",
        "signup": "Регистрация"
    },
    "en": {
        "welcome": "Welcome!",
        "descrdescription-singup": "Enter your details and register",
        "description-singin": "Please enter your login details.",
        "signin": "Sign In",
        "signup": "Sign Up"
    }
};

// При загрузке страницы: проверяем cookie и устанавливаем нужный язык
window.addEventListener("load", () => {
    const savedLang = getCookie("site_lang") || "en"; // по умолчанию русский
    updateContent(savedLang);

});