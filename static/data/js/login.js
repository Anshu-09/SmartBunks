document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#loginForm");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(form);

        try {
            const response = await fetch("/login", {
                method: "POST",
                body: formData
            });

            const message = await response.text(); 

            if (response.status === 401) {
                alert("❌ " + message);
            } else if (response.status === 404) {
                alert("⚠️ " + message);
            } else if (response.ok) {
                window.location.href = "/"; 
            } else {
                alert("Something went wrong.");
            }
        } catch (err) {
            console.error("Login request failed:", err);
            alert("Network error.");
        }
    });
});
