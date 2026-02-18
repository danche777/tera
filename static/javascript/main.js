// ----------------------  визуал  ----------------------
const cards = document.querySelectorAll('.card');
const indicator = document.getElementById('indicator');
const container = document.getElementById('container');


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

// ----------------------  функциональная составляющая  ----------------------

const getStartButton = document.getElementById("start")
const token = localStorage.getItem("token")


function swapPageTo(link) {
    getStartButton.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = link;
    });
}

console.log(token);
if (!token) {
    swapPageTo("/sign_in")
} else if (token) {
    swapPageTo('/forum')
}