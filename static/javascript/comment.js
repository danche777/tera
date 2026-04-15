const postContent = document.querySelector(".content_item_forum")
const postUsername = document.querySelector(".username")
const item_forum = document.querySelector(".item_forum")

postContent.textContent = localStorage.getItem("postContent")
postUsername.textContent = localStorage.getItem("postUsername")


document.title = postUsername.textContent + "'s post"

const submitBtn = document.querySelector(".submit_comment_button")

async function addComment() {
    const token = localStorage.getItem("token")
    const postId = localStorage.getItem("postId")
    const contentComment = document.getElementById("comment_content").value
    const response = await fetch("/add_comment", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            access_token: token,
            post_id: postId,
            comment: contentComment
        })
    });

    if (response.ok){
        location.reload();
    } else {
        // const data = await response.json();
        // DisplayErrorTooltip(data.message)
        alert('error')
    }
}

submitBtn.addEventListener("click", async function () {
    const contentComment = document.getElementById("comment_content")
    if (contentComment.value == "") {
        alert("Please enter a comment")
    } else {
        addComment()
    };
})



async function addReplyComment(commentId) {
    const token = localStorage.getItem("token")
    const postId = localStorage.getItem("postId")
    const contentComment = document.getElementById("comment_content").value
    const response = await fetch("/add_comment", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            access_token: token,
            post_id: postId,
            comment_id: commentId,
            comment: contentComment
        })
    });

    if (response.ok){
        location.reload();
    } else {
        // const data = await response.json();
        // DisplayErrorTooltip(data.message)
        alert('error')
    }
}


const replyButtton = document.querySelectorAll("#reply");
replyButtton.forEach(button => {
    button.onclick = function () {
        const commentId = button.name
        button.style.display = 'none';
        const comentItem = document.getElementById(commentId)
        const replySeparator = document.createElement("div")
        const replyBody = document.createElement("div")
        const replyTextarea = document.createElement("textarea")
        const replyBtnsConteiner = document.createElement("div")
        const replySubbmitBtn = document.createElement("button")
        const replyCloseBtn = document.createElement("button")

        replySubbmitBtn.textContent = "Submit"
        replyCloseBtn.textContent = "×"
        replyTextarea.maxLength = 200

        replyBody.className = "reply_body"
        replyTextarea.className = "reply_textarea"

        replySeparator.className = "reply_separator"
        replyBtnsConteiner.className = "reply_buttons_container"
        replySubbmitBtn.className = "reply_submit_button"
        replyCloseBtn.className = "reply_close_button"

        comentItem.appendChild(replySeparator)
        comentItem.appendChild(replyBody)
        replyBody.appendChild(replyTextarea)
        replyBody.appendChild(replyBtnsConteiner)
        replyBtnsConteiner.appendChild(replySubbmitBtn)
        replyBtnsConteiner.appendChild(replyCloseBtn)
        // const commentId = this.name;
        // addReplyComment(commentId);
    };
});