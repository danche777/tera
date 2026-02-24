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

    // 5. Добавляем стили (через JS для удобства, лучше вынести в CSS)
    const style = document.createElement('style');
    style.innerHTML = `
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            opacity: 0;
            animation: fadeIn 0.3s forwards;
        }

        .modal-content {
            background: white;
            padding: 20px;
            border-radius: 8px;
            width: 90%;
            max-width: 500px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            position: relative;
            transform: translateY(-20px);
            animation: slideIn 0.3s forwards;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }

        .close-modal {
            font-size: 24px;
            cursor: pointer;
            color: #aaa;
        }

        .close-modal:hover {
            color: #000;
        }

        .modal-body textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            resize: vertical;
            margin-bottom: 15px;
            font-family: inherit;
            box-sizing: border-box; /* Важно для корректной ширины */
        }

        .submit-post-btn {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            float: right;
        }

        .submit-post-btn:hover {
            background-color: #0056b3;
        }

        @keyframes fadeIn {
            to { opacity: 1; }
        }

        @keyframes slideIn {
            to { transform: translateY(0); }
        }
    `;
    document.head.appendChild(style);

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
        /*
        const token = localStorage.getItem("token");
        const response = await fetch("/create_post", {
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
        */
       
       console.log("Пост отправлен:", text);
       closeModal();
    };
}

// Навешиваем обработчик на кнопку
postButton.addEventListener("click", (e) => {
    e.preventDefault();
    showCreatePostModal();
});
