document.addEventListener("DOMContentLoaded", () => {
  const processButton = document.getElementById("process-button");
  const videoUrlInput = document.getElementById("video-url");
  const responseDiv = document.getElementById("response");
  const spinner = document.getElementById("spinner");
  const numTopicsSelect = document.getElementById("num-topicos"); // 🔹 novo

  // 🔹 Try to get the current tab URL if it's a YouTube video
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs.length > 0) {
      const activeTabUrl = tabs[0].url;
      if (activeTabUrl && activeTabUrl.includes("youtube.com/watch")) {
        videoUrlInput.value = activeTabUrl;
      }
    }
  });

  if (!processButton || !videoUrlInput || !responseDiv || !spinner || !numTopicsSelect) {
    console.error("Error: DOM elements not found.");
    return;
  }

  processButton.addEventListener("click", async () => {
    const videoUrl = videoUrlInput.value.trim();
    const numTopicos = parseInt(numTopicsSelect.value, 10); // 🔹 novo

    responseDiv.textContent = "";
    spinner.style.display = "block";

    if (!videoUrl) {
      responseDiv.textContent = "Please enter a video URL.";
      spinner.style.display = "none";
      return;
    }

    try {
      console.log("Número de tópicos selecionado:", numTopicos); // opcional para debug

      const response = await fetch("http://127.0.0.1:5000/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          video_url: videoUrl,
          num_topicos: numTopicos, // 🔹 agora o backend recebe isso
        }),
      });

      spinner.style.display = "none";

      if (response.ok) {
        const data = await response.json();

        // 🔹 Format and display topics
        const topicsArray = data.topics
          .split(/\d+\.\s+/) // Split based on "1. ", "2. ", etc.
          .filter(topic => topic.trim() !== "")
          .map((topic, index) => `<li><strong>${index + 1}:</strong> ${topic.trim()}</li>`);

        responseDiv.innerHTML = `<span class="success">Topics:</span><ul>${topicsArray.join("")}</ul>`;
      } else {
        const errorData = await response.json();
        responseDiv.innerHTML = `<span class="error">Error: ${errorData.error || "An error occurred while processing the video."}</span>`;
      }
    } catch (error) {
      spinner.style.display = "none";
      responseDiv.innerHTML = `<span class="error">Error connecting to the server.</span>`;
    }
  });
});
