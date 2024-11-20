document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("upload-form");
    const fileInput = document.getElementById("pdf-file");
    const statusMessage = document.getElementById("status-message");
    const loadingMessage = document.getElementById("loading-message");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        console.log("Form submission triggered");

        if (!fileInput.files.length) {
            alert("Please select a PDF file to upload.");
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append("file", file);

        loadingMessage.style.display = "block";
        statusMessage.textContent = "";

        try {
            console.log("Sending file to server...");
            const response = await fetch("http://127.0.0.1:8000/convert", {
                method: "POST",
                body: formData,
            });

            console.log("Response received:", response);

            if (!response.ok) {
                throw new Error("File conversion failed.");
            }

            const blob = await response.blob();
            console.log("Blob received:", blob);
            console.log("Received blob size:", blob.size);

            if (!blob.size) {
                throw new Error("Received empty file from the server.");
            }

            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = file.name.replace(".pdf", ".docx");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            statusMessage.textContent = "Conversion successful! Your file has been downloaded.";
            statusMessage.style.color = "green";

        } catch (error) {
            console.error("Error during conversion:", error.message);
            statusMessage.textContent = error.message || "An error occurred during conversion.";
            statusMessage.style.color = "red";
        } finally {
            loadingMessage.style.display = "none";
        }
    });
});
