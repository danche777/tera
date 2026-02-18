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