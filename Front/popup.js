document.addEventListener("DOMContentLoaded", () => {
  const processButton = document.getElementById("process-button");
  const videoUrlInput = document.getElementById("video-url");
  const responseDiv = document.getElementById("response");
  const spinner = document.getElementById("spinner");

  if (!processButton || !videoUrlInput || !responseDiv || !spinner) {
    console.error("Erro: Elementos do DOM não encontrados.");
    return;
  }

  processButton.addEventListener("click", async () => {
    const videoUrl = videoUrlInput.value.trim();
    responseDiv.textContent = "";
    spinner.style.display = "block";

    if (!videoUrl) {
      responseDiv.textContent = "Por favor, insira uma URL.";
      spinner.style.display = "none";
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_url: videoUrl })
      });

      spinner.style.display = "none";

      if (response.ok) {
        const data = await response.json();
        
        // 🔹 Ajuste: Separar os tópicos corretamente
        const topicsArray = data.topics
          .split(/\d+\.\s+/) // Divide os tópicos baseados em "1. ", "2. ", etc.
          .filter(topic => topic.trim() !== "") // Remove espaços em branco
          .map((topic, index) => `<li><strong>${index + 1}:</strong> ${topic.trim()}</li>`) // Formata corretamente

        responseDiv.innerHTML = `<span class="success">Tópicos:</span><ul>${topicsArray.join("")}</ul>`;
      } else {
        const errorData = await response.json();
        responseDiv.innerHTML = `<span class="error">Erro: ${errorData.error || "Erro ao processar o vídeo."}</span>`;
      }
    } catch (error) {
      spinner.style.display = "none";
      responseDiv.innerHTML = `<span class="error">Erro ao conectar ao servidor.</span>`;
    }
  });
});
