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

async function getUser() {
    const token = localStorage.getItem("token")
    const response = await fetch("/get_user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            access_token: token
        })
    });
}

function logout() {
    const token = localStorage.getItem("token");
    if (token) {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        location.href = "/";
    }
}