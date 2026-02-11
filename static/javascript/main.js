// ----------------------  main.js  ----------------------
const cards = document.querySelectorAll('.card');
const indicator = document.getElementById('indicator');
const container = document.getElementById('container');

if (cards && container && indicator) {
    /* Физика движения */
    let currentX = 0;
    let currentY = 0;
    let targetX = 0;
    let targetY = 0;
    let velocityX = 0;
    let velocityY = 0;

    const stiffness = 0.06; // скорость
    const damping = 0.76;   // инерция

    function animate() {
        const forceX = (targetX - currentX) * stiffness;
        velocityX = (velocityX + forceX) * damping;
        currentX += velocityX;

        const forceY = (targetY - currentY) * stiffness;
        velocityY = (velocityY + forceY) * damping;
        currentY += velocityY;

        indicator.style.transform = `translate(${currentX}px,${currentY}px) scaleX(1.1) scaleY(1.2)`;
        requestAnimationFrame(animate);
    }

    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            indicator.classList.remove('hidden');
            const cardRect = card.getBoundingClientRect();
            const containerRect = container.getBoundingClientRect();
            targetX = cardRect.left - containerRect.left;
            targetY = cardRect.top - containerRect.top;
        });
    });

    container.addEventListener('mouseleave', () => {
        indicator.classList.add('hidden');
    });

    const firstRect = cards[0].getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    currentX = targetX = firstRect.left - containerRect.left;
    currentY = targetY = firstRect.top - containerRect.top;

    animate();
} else {
    console.warn('Элементы .card, #container или #indicator не найдены на странице!');
}


// ----------------------  sign-in/sign-up  ----------------------
// JS для показа/скрытия пароля с глазком
const eyeBtn = document.getElementById('eye-btn');
const passwordInput = document.getElementById('password');

if (eyeBtn && passwordInput) {
    eyeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const isPassword = passwordInput.getAttribute('type') === 'password';
        passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
        eyeBtn.textContent = isPassword ? '⌣' : '👁';
    });
}

// JS для кнопки confirm_btn
const button = document.querySelector('.confirm_btn');
const username = document.getElementById('username');
const password = document.getElementById('password');

if (button && username && password) {
    button.addEventListener('click', () => {
    if (!username.value || !password.value) {
        // красная подсветка
        button.style.boxShadow = '0 8px 24px rgba(255,0,0,0.5), 0 0 10px rgba(255,0,0,0.3) inset';

        // создаём tooltip если его нет
        if (!button.querySelector('.tooltip')) {
            const tooltip = document.createElement('div');
            tooltip.classList.add('tooltip');
            tooltip.innerText = 'Enter text';
            button.appendChild(tooltip);
        }

        // показываем tooltip
        button.classList.add('show-tooltip');

        // скрываем через 1.2 секунды
        setTimeout(() => {
            button.classList.remove('show-tooltip');
            button.style.boxShadow = '0 8px 24px rgba(0,0,0,0.2), 0 0 15px rgba(255,255,255,0.2) inset';
        }, 1200);

        return;
    }

    // успешная анимация
    button.innerText = 'Confirm';
    button.style.boxShadow = '0 8px 24px rgba(0,255,0,0.5), 0 0 10px rgba(0,255,0,0.3) inset';
    
    setTimeout(() => {
        button.innerText = 'Confirm';
        button.style.boxShadow = '0 8px 24px rgba(0,0,0,0.2), 0 0 15px rgba(255,255,255,0.2) inset';
        username.value = '';
        password.value = '';
        passwordInput.setAttribute('type', 'password');
        eyeBtn.textContent = '👁';
    }, 1500);
    });
}
