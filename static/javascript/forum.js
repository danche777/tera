// Получаем кнопку открытия
const postButton = document.querySelector(".strt_post_button");

// Функция создания и показа модального окна
function showCreatePostModal() {
    // Проверяем, есть ли уже окно, чтобы не создавать дубликаты
    if (document.getElementById('post-modal')) return;

    // 1. Создаем элементы DOM
    const modalOverlay = document.createElement('div');
    const modalContent = document.createElement('div');
    const modalHeader = document.createElement('div');
    const modalTitle = document.createElement('h2');
    const closeBtn = document.createElement('span');
    const modalBody = document.createElement('div');
    const textarea = document.createElement('textarea');
    const submitBtn = document.createElement('button');

    // 2. Добавляем классы и атрибуты
    modalOverlay.id = 'post-modal';
    modalOverlay.className = 'modal-overlay';
    
    modalContent.className = 'modal-content';
    
    modalHeader.className = 'modal-header';
    
    modalTitle.textContent = 'Создать пост';
    
    closeBtn.className = 'close-modal';
    closeBtn.innerHTML = '&times;';
    
    modalBody.className = 'modal-body';
    
    textarea.id = 'post-text';
    textarea.placeholder = 'Введите текст вашего поста...';
    textarea.rows = 5;
    
    submitBtn.className = 'submit-post-btn';
    submitBtn.textContent = 'Опубликовать';

    // 3. Собираем структуру
    modalHeader.appendChild(modalTitle);
    modalHeader.appendChild(closeBtn);
    
    modalBody.appendChild(textarea);
    modalBody.appendChild(submitBtn);
    
    modalContent.appendChild(modalHeader);
    modalContent.appendChild(modalBody);
    
    modalOverlay.appendChild(modalContent);

    // 4. Добавляем в body
    document.body.appendChild(modalOverlay);

    // 6. Логика закрытия
    const closeModal = () => {
        modalOverlay.style.opacity = '0';
        modalContent.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            if (document.getElementById('post-modal')) {
                document.body.removeChild(modalOverlay);
            }
        }, 300); // Время должно совпадать с анимацией
    };

    closeBtn.onclick = closeModal;
    
    // Закрытие по клику на затемненный фон
    modalOverlay.onclick = (e) => {
        if (e.target === modalOverlay) {
            closeModal();
        }
    };

    // 7. Логика отправки (пример)
    submitBtn.onclick = async () => {
        const text = textarea.value;
        if (!text.trim()) {
            alert("Пост не может быть пустым!"); // Или используйте вашу систему уведомлений
            return;
        }

        // Раскомментируйте и адаптируйте для реального запроса

        const token = localStorage.getItem("token");
        const response = await fetch("/add_post", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                access_token: token,
                content: text
            })
        });

        if (response.ok) {
            closeModal();
            // Логика обновления списка постов
        }

       
       console.log("Пост отправлен:", text);
       closeModal();
    };
}

// Навешиваем обработчик на кнопку
postButton.addEventListener("click", (e) => {
    e.preventDefault();
    showCreatePostModal();
});
