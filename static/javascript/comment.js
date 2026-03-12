const postContent = document.querySelector(".content_item_forum")
const postUsername = document.querySelector(".username")
const item_forum = document.querySelector(".item_forum")

item_forum.id = localStorage.getItem("postId")
postContent.textContent = localStorage.getItem("postContent")
postUsername.textContent = localStorage.getItem("postUsername")


document.title = postUsername.textContent + "'s post"

const submitBtn = document.querySelector(".submit_comment_button")

async function addComent() {
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
        addComent()
    };
})