document.addEventListener("DOMContentLoaded", () => {
  const processButton = document.getElementById("process-button");
  const videoUrlInput = document.getElementById("video-url");
  const languageSelect = document.getElementById("language");
  const topicsSelect = document.getElementById("num-topicos"); // Seletor de tópicos
  const responseDiv = document.getElementById("response");
  const spinner = document.getElementById("spinner");

  // Capturar a URL da aba ativa e preencher o campo se for do YouTube
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs.length > 0) {
      const activeTabUrl = tabs[0].url;
      console.log("🔍 URL capturada:", activeTabUrl); // Debug no console

      if (activeTabUrl.includes("youtube.com/watch")) {
        videoUrlInput.value = activeTabUrl;
        console.log("✅ URL do YouTube detectada e inserida!");
      } else {
        console.log("⚠ URL não é de um vídeo do YouTube.");
      }
    } else {
      console.log("❌ Nenhuma aba ativa encontrada!");
    }
  });

  processButton.addEventListener("click", async () => {
    const videoUrl = videoUrlInput.value.trim();
    const language = languageSelect.value;
    const numTopicos = topicsSelect.value; // Captura a quantidade de tópicos escolhida

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
        body: JSON.stringify({
          video_url: videoUrl,
          language: language,
          num_topicos: parseInt(numTopicos) // Envia para o backend
        })
      });

      spinner.style.display = "none";

      if (response.ok) {
        const data = await response.json();
        const topicsList = data.topics
          .split(/\d+\.\s+/)
          .filter(topic => topic.trim() !== "")
          .map((topic, index) => `<li><strong>${index + 1}:</strong> ${topic.trim()}</li>`)
          .join("");

        responseDiv.innerHTML = `<span class="success">Tópicos:</span><ul>${topicsList}</ul>`;
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
