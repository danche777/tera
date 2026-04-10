document.addEventListener("DOMContentLoaded", async function () {
    const token = localStorage.getItem("token");
    if (token) {
        const response = await fetch("/check_token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                access_token: token
            })
        });

        if (!response.ok) {
            localStorage.removeItem("token");
            localStorage.removeItem("username")
            this.location.href= '/sign_in'
        };
    };
});