// переменные для ошибок и отправки
const button = document.querySelector('.confirm_btn');
const username = document.getElementById('username');
const password = document.getElementById('password');

//  переменные для глаза
const eyeBtn = document.getElementById('eye-btn');
const passwordInput = document.getElementById('password');

// переменная для подсказки ToolTip
let tooltip = document.createElement('div');

// скрытие/показ пароля
eyeBtn.addEventListener('click', (e) => {
    e.preventDefault();
    const isPassword = passwordInput.getAttribute('type') === 'password';
    passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
    eyeBtn.textContent = isPassword ? '⌣' : '👁';
});

// спрятать ToolTip через 1.2 секунды
function hideTooltip() {
    setTimeout(() => {
        button.classList.remove('show-tooltip');
        button.style.boxShadow = '0 8px 24px rgba(0,0,0,0.2), 0 0 15px rgba(255,255,255,0.2) inset';
    }, 1200);
}

// вывод ошибок для ToolTip
function DisplayErrorTooltip(text) {
    // красная подсветка
    button.style.boxShadow = '0 8px 24px rgba(255,0,0,0.5), 0 0 10px rgba(255,0,0,0.3) inset';
    // текст tooltip  
    tooltip.innerText = text;
    // показываем tooltip
    button.classList.add('show-tooltip');
    // показываем его на 1.2 секунды и прячем
    hideTooltip()
}

// отправка пароля|имени на сервер и перенос на главную странницу или же вывод ошибки
async function auth() {
    const response = await fetch("/auth", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            username: username.value,
            password: password.value
        })
    });

    if (response.ok) {
    const data = await response.json();
    localStorage.setItem("token", data.access_token);
    window.location.href = "/";
    } else {
    const data = await response.json();
    DisplayErrorTooltip(data.message)
    }
}

// обработчик всех ошибок для кнопки
button.addEventListener('click', () => {
    // создаём tooltip если его нет
    if (!button.querySelector('.tooltip')) {
        tooltip.classList.add('tooltip');
        button.appendChild(tooltip);
    };
        // проверка пусты ли поля
    if (!username.value || !password.value) {
        DisplayErrorTooltip('Enter text');
    } else if (username.value.length <= 1) {
        DisplayErrorTooltip('name <= 1');
    } else if (username.value.length >= 16) {
        DisplayErrorTooltip('username >= 16');
    } else if (password.value.length < 8) {
        DisplayErrorTooltip('password < 8');
    } else if (password.value.length >= 16) {
        DisplayErrorTooltip('password >= 16');
    } else {
        auth()
    }
});