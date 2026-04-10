const account_delete_buttons = document.querySelectorAll(".account_delete_button");

const upvouteButton = document.querySelectorAll("#upvoute");
account_delete_buttons.forEach(button => {
    button.onclick = function () {
        const postContainer = this.closest('.item_forum');
        const postId = postContainer.id
        if (postId) {
            deletePost(postId)
        }
    };
});

async function deletePost(postId) {
    const response = await fetch("/delete_post/{postId}", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            post_id: postId,
            access_token: localStorage.getItem("token")
        })
    });
    if (response.ok) {
        location.reload()
    } else {
        alert('error')
    };
};

function logout() {
    const token = localStorage.getItem("token");
    if (token) {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        window.location.href = "/";
    }
}

const commentButtons = document.querySelectorAll(".comments_button");
commentButtons.forEach(button => {
    button.onclick = function () {
        const Id = this.id; // ID кнопки совпадает с ID поста
        const postContainer = this.closest('.item_forum');
        const contentElement = postContainer.querySelector('.content_item_forum');
        if (Id && contentElement) {
            const postId = this.id;
            const postContent = contentElement.textContent;
            const postUsername = localStorage.getItem("username");
            localStorage.setItem("postContent", postContent);
            localStorage.setItem("postUsername", postUsername);
            localStorage.setItem("postId", postId);
            window.location.href = `/comments/${postId}`;
        };
    };
});