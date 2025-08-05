const langStrings = {
    "ru": {
        "welcome": "Добро пожаловать!",
        "description-singup": "Введите свои данные и зарегистрируйтесь",
        "description-singin": "Введите свои данные для входа в систему",
        "signin": "Войти",
        "signup": "Зарегистрироваться",
        "registration": "Регистрация", 
        "forget": "Забыли пароль?"
    },
    "en": {
        "welcome": "Welcome!",
        "description-singup": "Enter your details and register",
        "description-singin": "Please enter your login details.",
        "signin": "Sign In",
        "signup": "Sign Up",
        "registration": "Регистрация", 
        "forget": "Forgot your password?"
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
    const savedLang = getCookie("site_lang") || "ru";
    updateContent(savedLang);

    const langSelect = document.getElementById("langSelect");
    if (langSelect) langSelect.value = savedLang;

    langSelect.addEventListener("change", function () {
        const selectedLang = this.value;
        setLanguage(selectedLang);
    });
};

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