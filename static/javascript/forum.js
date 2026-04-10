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
    textarea.maxLength = 500
    
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
            alert("Пост не может быть пустым!");
            return;
        }

        try {
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
                // Перезагрузка только при успешном ответе
                location.reload();
            } else {
                const error = await response.text();
                console.error("Ошибка сервера:", error);
                alert("Не удалось опубликовать пост");
            }

        } catch (err) {
            console.error("Ошибка запроса:", err);
            alert("Ошибка соединения с сервером");
        }
    };
}

// Навешиваем обработчик на кнопку
postButton.addEventListener("click", (e) => {
    e.preventDefault();
    showCreatePostModal();
});


// открытие комментариев
const commentButtons = document.querySelectorAll(".comments_button");
commentButtons.forEach(button => {
    button.onclick = function () {
        const Id = this.id; // ID кнопки совпадает с ID поста
        const postContainer = this.closest('.item_forum');
        const contentElement = postContainer.querySelector('.content_item_forum');
        const usernameElement = postContainer.querySelector('.username');
        if (Id && contentElement) {
            const postId = this.id;
            const postContent = contentElement.textContent;
            const postUsername = usernameElement.textContent;
            localStorage.setItem("postContent", postContent);
            localStorage.setItem("postUsername", postUsername);
            localStorage.setItem("postId", postId);
            window.location.href = `/comments/${postId}`;
        };
    };
});


async function like(postId) {
    const token = localStorage.getItem("token")
    const like = "1"

    const response = await fetch("/add_reaction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            post_id: postId,
            access_token: token,
            reaction: like
        })
    });

    if (!response.ok) {
        alert('error')
    } else (
        location.reload()
    )
};

async function dislike(postId) {
    const token = localStorage.getItem("token")
    const like = "-1"

    const response = await fetch("/add_reaction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            post_id: postId,
            access_token: token,
            reaction: like
        })
    });

    if (!response.ok) {
        alert('error')
    } else (
        location.reload()
    )
};


// лайк
const upvouteButton = document.querySelectorAll("#upvoute");
upvouteButton.forEach(button => {
    button.onclick = function () {
        const postId = this.name; // ID кнопки совпадает с ID поста
        const postContainer = this.closest('.item_forum');
        const contentElement = postContainer.querySelector('.upvoute_button');
        // const usernameElement = postContainer.querySelector('.username');
        if (postId && contentElement) {
            like(postId);
        };
    };
});

// дизлайк
const downvouteButton = document.querySelectorAll("#downvoute");
downvouteButton.forEach(button => {
    button.onclick = function () {
        const postId = this.name; // ID кнопки совпадает с ID поста
        const postContainer = this.closest('.item_forum');
        const contentElement = postContainer.querySelector('.upvoute_button');
        if (postId && contentElement) {
            dislike(postId)
        };
    };
});


async function left_facing() {
    const response = await fetch("/add_reaction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            moution: 'left'
        })
    });

    if (!response.ok) {
        alert('error')
    } else (
        location.reload()
    )
}

function page_moving(direction) {
    const urlParams = new URL(window.location.href)

    var page_number = Number(urlParams.searchParams.get('page_number')) + direction

    urlParams.searchParams.set('page_number', page_number);
    window.location.href = urlParams.toString()
}