# 🎓 ExtensaoGPT

A backend application that uses the OpenAI API to extract the **most important topics** from educational YouTube videos. Designed for students, researchers, and content creators who want a fast, AI-powered summary of what a video covers.

---

## 🌍 Overview

**ExtensaoGPT** powers a browser extension popup. The workflow is simple: you select a YouTube video (and how many topics you want), and the backend handles the heavy lifting:

1.  **Downloads** the audio from YouTube.
2.  **Transcribes** it using OpenAI’s Speech-to-Text (Whisper).
3.  **Extracts** the top *X* most important topics using GPT-4.
4.  **Returns** a clean JSON response ready to render in the UI.

---

## 🚀 Features

* 🔗 **YouTube Audio Download:** Uses `yt-dlp` to fetch the best available audio.
* 🎙️ **Automatic Transcription:** Leverages OpenAI Audio API (`whisper-1`).
* 🧠 **Topic Extraction:** Uses **GPT-4** to summarize content into a configurable number of topics (5, 7, 10, etc.).
* ⚙️ **Optimized Pipeline:**
    * Audio splitting with `ffmpeg`.
    * Parallel segment transcription for long videos.
    * Chunk-based topic extraction and consolidation.
* 🧪 **JSON API:** Returns structured data for easy integration with browser extensions.

---

## 🛠️ Tech Stack

* **Python 3**
* **Flask** + **Flask-CORS** (HTTP API)
* **OpenAI API** (`whisper-1` & `gpt-4`)
* **yt-dlp** (Media download)
* **ffmpeg** (Audio segmentation/conversion)
* **python-dotenv** (Environment variable management)

---

## 📁 Project Structure

```text
ExtensaoGPT/
├─ Back/
│  ├─ main.py            # Flask server (entrypoint)
│  ├─ transcricao.py     # Download + segmentation + transcription
│  ├─ topicos.py         # GPT-4 topic extraction
│  ├─ .env               # API Keys (not committed)
│  └─ requirements.txt   # Python dependencies
└─ Front/
   ├─ manifest.json      # Extension manifest
   ├─ popup.html         # Extension UI
   ├─ popup.js           # Client-side logic
   └─ style.css          # Styling
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone <your_repo_url>
cd ExtensaoGPT/Back
```

### 2. Create a virtual environment (Optional)
```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1
# Mac/Linux
source .venv/bin/activate
```

### 3. Install Python dependencies
```bash
pip install flask flask-cors openai python-dotenv yt-dlp
```

### 4. Install FFmpeg
**Required:** You must have a working `ffmpeg` executable for audio segmentation.
1.  Download an ffmpeg essentials build.
2.  Add the `bin` folder to your system **PATH**, OR configure the full path in `transcricao.py`.

### 5. Configure environment variables
Create a `.env` file in the `Back/` folder:
```ini
OPENAI_API_KEY=your_openai_api_key_here
```

---

## ▶️ Running the Backend

From the `Back/` folder:

```bash
python main.py
```

* **Server runs at:** `http://127.0.0.1:5000`
* **Endpoint:** `POST /process`

---

## 🔌 API Endpoint

### `POST /process`

**Request Body:**
```json
{
  "video_url": "[https://www.youtube.com/watch?v=XXXX](https://www.youtube.com/watch?v=XXXX)",
  "num_topicos": 7
}
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `video_url` | string | The full YouTube video URL. |
| `num_topicos` | int | (Optional) Number of topics to extract. Defaults to 7. |

**Response (Success):**
```json
{
  "topics": "1. Topic one\n2. Topic two\n3. Topic three\n..."
}
```

**Response (Error):**
```json
{
  "error": "Error message details"
}
```

---

## 🧠 How It Works (Pipeline)

1.  **Download:** `transcricao.py` uses `yt-dlp` to download audio to `work/audio.<ext>`.
2.  **Segment & Transcribe:**
    * Splits audio into segments using `ffmpeg`.
    * Transcribes segments in parallel (`ThreadPoolExecutor`) using `whisper-1`.
    * Concatenates segments into a full text string.
3.  **Extract Topics:** `topicos.py` chunks the text (to manage token limits), runs GPT-4 on each chunk, and consolidates the results into a final numbered list.

---

## 🧩 Possible Improvements

- [ ] Add caching by YouTube Video ID (avoid re-processing).
- [ ] Support for multiple output languages.
- [ ] Stream progress updates (Download → Transcribe → Summarize) via WebSocket.

<br>
<br>

---
---

<br>
<br>

# 🎓 ExtensaoGPT (Português)

Uma aplicação backend que utiliza a API da OpenAI para extrair os **principais tópicos** de vídeos educacionais do YouTube. Ideal para estudantes, pesquisadores e criadores de conteúdo que desejam um resumo rápido e inteligente dos vídeos assistidos.

---

## 🌍 Visão Geral

O **ExtensaoGPT** é o backend que alimenta uma extensão de navegador. O fluxo de uso é simples: você seleciona um vídeo do YouTube (e quantos tópicos deseja), e o backend realiza o seguinte processo:

1.  **Baixa** o áudio do YouTube.
2.  **Transcreve** o conteúdo com o Speech-to-Text da OpenAI (Whisper).
3.  **Extrai** os *X* tópicos mais importantes usando o GPT-4.
4.  **Retorna** uma resposta em JSON pronta para ser exibida na extensão.

---

## 🚀 Funcionalidades

* 🔗 **Download de Áudio:** Utiliza `yt-dlp` para baixar o melhor áudio disponível.
* 🎙️ **Transcrição Automática:** Utiliza a API `whisper-1` da OpenAI.
* 🧠 **Extração de Tópicos:** Usa o **GPT-4** para identificar pontos chave (configurável: 5, 7, 10 tópicos, etc.).
* ⚙️ **Pipeline Otimizada:**
    * Segmentação de áudio com `ffmpeg`.
    * Transcrição paralela de segmentos para vídeos longos.
    * Consolidação de tópicos em blocos.
* 🧪 **API JSON:** Retorno estruturado para fácil integração com frontends.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3**
* **Flask** + **Flask-CORS** (API HTTP)
* **OpenAI API** (`whisper-1` e `gpt-4`)
* **yt-dlp** (Download de mídia)
* **ffmpeg** (Segmentação e conversão de áudio)
* **python-dotenv** (Gerenciamento de variáveis de ambiente)

---

## 📁 Estrutura do Projeto

```text
ExtensaoGPT/
├─ Back/
│  ├─ main.py            # Servidor Flask (ponto de entrada)
│  ├─ transcricao.py     # Download + segmentação + transcrição
│  ├─ topicos.py         # Extração de tópicos com GPT-4
│  ├─ .env               # Chave da API (não versionado)
│  └─ requirements.txt   # Dependências Python
└─ Front/
   ├─ manifest.json      # Manifesto da extensão
   ├─ popup.html         # UI do popup
   ├─ popup.js           # Lógica do cliente
   └─ style.css          # Estilos
```

---

## ⚙️ Instalação e Configuração

### 1. Clonar o repositório
```bash
git clone <seu_repo_url>
cd ExtensaoGPT/Back
```

### 2. Criar ambiente virtual (Opcional)
```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1
# Mac/Linux
source .venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install flask flask-cors openai python-dotenv yt-dlp
```

### 4. Instalar FFmpeg
**Obrigatório:** É necessário ter o executável do `ffmpeg` para a segmentação de áudio.
1.  Baixe um build do ffmpeg.
2.  Adicione a pasta `bin` ao **PATH** do sistema, OU configure o caminho absoluto no arquivo `transcricao.py`.

### 5. Configurar variáveis de ambiente
Crie um arquivo `.env` na pasta `Back/`:
```ini
OPENAI_API_KEY=sua_chave_da_openai_aqui
```

---

## ▶️ Executando o Backend

A partir da pasta `Back/`:

```bash
python main.py
```

* **Servidor roda em:** `http://127.0.0.1:5000`
* **Endpoint:** `POST /process`

---

## 🔌 Endpoint da API

### `POST /process`

**Corpo da Requisição (JSON):**
```json
{
  "video_url": "[https://www.youtube.com/watch?v=XXXX](https://www.youtube.com/watch?v=XXXX)",
  "num_topicos": 7
}
```

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| `video_url` | string | URL completa do vídeo do YouTube. |
| `num_topicos` | int | (Opcional) Quantidade de tópicos a extrair. Padrão: 7. |

**Resposta (Sucesso):**
```json
{
  "topics": "1. Tópico um\n2. Tópico dois\n3. Tópico três\n..."
}
```

**Resposta (Erro):**
```json
{
  "error": "Mensagem detalhada do erro"
}
```

---

## 🧠 Como Funciona (Pipeline)

1.  **Download:** O script `transcricao.py` usa o `yt-dlp` para baixar o áudio em `work/audio.<ext>`.
2.  **Segmentação e Transcrição:**
    * O áudio é dividido em partes menores usando `ffmpeg`.
    * Cada parte é transcrita em paralelo (`ThreadPoolExecutor`) via `whisper-1`.
    * Os segmentos são concatenados numa string final.
3.  **Extração de Tópicos:** O script `topicos.py` divide o texto em *chunks* (para respeitar limites de tokens), roda o GPT-4 em cada parte e consolida o resultado numa lista final.

---

## 🧩 Possíveis Melhorias

- [ ] Cache por ID do vídeo (evitar reprocessamento).
- [ ] Suporte para múltiplos idiomas de saída.
- [ ] Streaming de progresso (Download → Transcrição → Resumo) via WebSocket.
