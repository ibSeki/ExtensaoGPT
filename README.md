# 🎓 ExtensaoGPT

A backend application that uses the OpenAI API to extract the **most important topics** from educational YouTube videos. Designed for students, researchers, and content creators who want a fast, AI-powered overview of what a video covers.

> 🔐 **Security note:** never commit API keys. If you ever pasted an API key in a public place, rotate it immediately.

---

## 🌍 Overview

**ExtensaoGPT** powers a browser extension popup. The workflow is simple: you select a YouTube video (and how many topics you want), and the backend handles the heavy lifting:

1. **Starts an async job** for a YouTube video (and desired topic count).
2. **Downloads** the audio from YouTube.
3. **Transcribes** it using OpenAI’s **speech-to-text (Audio Transcriptions)** API (model configurable).
4. **Extracts** the top *X* most important topics using a GPT model (e.g., GPT-4).
5. **Tracks progress** via a job status endpoint so the UI can keep updating even if the popup closes.

---

## 🚀 Features

* 🔗 **YouTube Audio Download:** Uses `yt-dlp` to fetch the best available audio (with multiple extraction strategies for improved reliability).
* 🎙️ **Automatic Transcription:** Uses OpenAI **Audio Transcriptions (speech-to-text)** API (transcription model configurable via environment variables).
* 🧠 **Topic Extraction:** Uses **GPT** (e.g., GPT-4) to summarize content into a configurable number of topics (5, 7, 10, etc.).
* ⚙️ **Optimized Pipeline:**
  * Audio splitting + conversion with `ffmpeg` (segments reduce request size and improve stability).
  * Configurable transcription concurrency and retry policy.
  * Chunk-based topic extraction and consolidation.
* 🧪 **Async Job API + Progress:**
  * `POST /process` returns **202 + job_id** immediately.
  * `GET /status/<job_id>` returns status (`queued`, `running`, `done`, `error`), progress %, and results.
* 🗃️ **Caching (optional):** Results can be cached by `(video_url, topic_budget)` to avoid recomputation on repeated requests.
* 🧩 **Extension-friendly JSON:** Designed for easy integration with a browser extension UI.

---

## 🛠️ Tech Stack

* **Python 3**
* **Flask** + **Flask-CORS** (HTTP API)
* **OpenAI API**
  * **Audio Transcriptions (speech-to-text)**
  * **Chat Completions** (topic extraction)
* **yt-dlp** (Media download)
* **ffmpeg** (Audio segmentation/conversion)
* **python-dotenv** (Environment variable management)

---

## 📁 Project Structure

```text
ExtensaoGPT/
├─ Back/
│  ├─ main.py            # Flask server (async job API)
│  ├─ transcricao.py     # Download + segmentation + transcription
│  ├─ topicos.py         # GPT topic extraction
│  ├─ .env               # API keys and settings (not committed)
│  ├─ requirements.txt   # Python dependencies
│  └─ work/
│     ├─ cache/          # Cached results (optional)
│     └─ jobs.json       # Persisted job status (best-effort)
└─ Front/
   ├─ manifest.json      # Extension manifest
   ├─ popup.html         # Extension UI
   ├─ popup.js           # Client-side logic (starts job + polls status)
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

Preferred:
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install flask flask-cors openai python-dotenv yt-dlp
```

### 4. Install FFmpeg

**Required:** You must have a working `ffmpeg` executable for audio segmentation/conversion.

1. Download an ffmpeg build.
2. Add the `bin` folder to your system **PATH**, OR set the full path using `FFMPEG_PATH` in `.env`.

### 5. Configure environment variables

Create a `.env` file in the `Back/` folder:
```ini
OPENAI_API_KEY=your_openai_api_key_here

# Optional (recommended)
FFMPEG_PATH=/path/to/ffmpeg

# Transcription behavior
TRANSCRIBE_MODEL=gpt-4o-mini-transcribe
TRANSCRIBE_SEGMENT_SECONDS=480
TRANSCRIBE_WORKERS=1
TRANSCRIBE_MAX_RETRIES=6

# Backend concurrency
MAX_JOBS=2

# Optional: helps yt-dlp on restricted videos (chrome|edge|firefox)
YTDLP_COOKIES_FROM_BROWSER=chrome
```

---

## ▶️ Running the Backend

From the `Back/` folder:

```bash
python main.py
```

* **Server runs at:** `http://127.0.0.1:5000`
* **Health check:** `GET /health`
* **Start job:** `POST /process`
* **Check status/results:** `GET /status/<job_id>`

---

## 🔌 API Endpoint

### `POST /process` (start async job)

**Request Body:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=XXXX",
  "num_topicos": 7
}
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `video_url` | string | The full YouTube video URL. |
| `num_topicos` | int | (Optional) Number of topics to extract. Defaults to 7. |

**Response (Accepted - 202):**
```json
{
  "job_id": "e9a1675f-3452-4560-afab-9f9642529740",
  "status": "queued"
}
```

### `GET /status/<job_id>` (poll job status)

**Response (Running):**
```json
{
  "status": "running",
  "progress": 35,
  "step": "transcribing",
  "video_url": "https://www.youtube.com/watch?v=XXXX",
  "num_topics": 7
}
```

**Response (Done):**
```json
{
  "status": "done",
  "progress": 100,
  "topics": "1. Topic one\n2. Topic two\n3. Topic three\n...",
  "step": "done"
}
```

**Response (Error):**
```json
{
  "status": "error",
  "progress": 100,
  "error": "Error message details"
}
```

---

## 🧠 How It Works (Pipeline)

1. **Start job:** `main.py` receives `POST /process`, creates a `job_id`, and returns immediately (`HTTP 202`).
2. **Download:** `transcricao.py` uses `yt-dlp` to download audio to `work/audio.<ext>` (optional cookies for restricted videos).
3. **Segment & Transcribe:**
   * Splits/converts audio into segments using `ffmpeg`.
   * Transcribes each segment using OpenAI **Audio Transcriptions (speech-to-text)**.
   * Supports configurable workers and retry/backoff.
4. **Extract Topics:** `topicos.py` chunks the text (to manage token limits), extracts candidate topics, and consolidates the results into a final numbered list.

---

## 🧩 Possible Improvements

- [ ] Add caching by YouTube Video ID (avoid re-processing).
- [ ] Support for multiple output languages.
- [ ] Stream progress updates (Download → Transcribe → Summarize) via WebSocket / SSE (instead of polling).
- [ ] Add optional timestamps per topic for better navigation.
- [ ] Add a deployable mode (Docker + production WSGI server).

<br>
<br>

---
---

<br>
<br>

# 🎓 ExtensaoGPT (Português)

Uma aplicação backend que utiliza a API da OpenAI para extrair os **principais tópicos** de vídeos educacionais do YouTube. Ideal para estudantes, pesquisadores e criadores de conteúdo que desejam um resumo rápido e inteligente do que um vídeo aborda.

> 🔐 **Nota de segurança:** nunca versione chaves de API. Se uma chave foi exposta, faça a rotação imediatamente.

---

## 🌍 Visão Geral

O **ExtensaoGPT** é o backend que alimenta uma extensão de navegador. O fluxo de uso é simples: você seleciona um vídeo do YouTube (e quantos tópicos deseja), e o backend realiza o seguinte processo:

1. **Inicia um job assíncrono** para o vídeo do YouTube (e a quantidade de tópicos).
2. **Baixa** o áudio do YouTube.
3. **Transcreve** usando a API de **Audio Transcriptions (speech-to-text)** da OpenAI (modelo configurável).
4. **Extrai** os *X* tópicos mais importantes usando um modelo GPT (ex.: GPT-4).
5. **Acompanha o progresso** via endpoint de status, permitindo que o job continue mesmo se o popup fechar.

---

## 🚀 Funcionalidades

* 🔗 **Download de Áudio:** Utiliza `yt-dlp` para baixar o melhor áudio disponível (com múltiplas estratégias para melhorar confiabilidade).
* 🎙️ **Transcrição Automática:** Utiliza a API de **Audio Transcriptions (speech-to-text)** da OpenAI (modelo configurável por variáveis de ambiente).
* 🧠 **Extração de Tópicos:** Usa um modelo **GPT** (ex.: GPT-4) para gerar tópicos (configurável: 5, 7, 10 etc.).
* ⚙️ **Pipeline Otimizado:**
  * Segmentação + conversão de áudio com `ffmpeg` (segmentos menores aumentam estabilidade).
  * Concorrência e política de retry configuráveis na transcrição.
  * Extração de tópicos por *chunks* e consolidação final.
* 🧪 **API Assíncrona com Progresso:**
  * `POST /process` retorna **202 + job_id** imediatamente.
  * `GET /status/<job_id>` retorna status (`queued`, `running`, `done`, `error`), progresso (%) e resultados.
* 🗃️ **Cache (opcional):** pode armazenar resultados por `(video_url, num_topicos)` para evitar reprocessamento.
* 🧩 **API JSON:** retorno estruturado para fácil integração com frontends/extensão.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3**
* **Flask** + **Flask-CORS** (API HTTP)
* **OpenAI API**
  * **Audio Transcriptions (speech-to-text)**
  * **Chat Completions** (extração de tópicos)
* **yt-dlp** (Download de mídia)
* **ffmpeg** (Segmentação e conversão de áudio)
* **python-dotenv** (Gerenciamento de variáveis de ambiente)

---

## 📁 Estrutura do Projeto

```text
ExtensaoGPT/
├─ Back/
│  ├─ main.py            # Servidor Flask (API assíncrona)
│  ├─ transcricao.py     # Download + segmentação + transcrição
│  ├─ topicos.py         # Extração de tópicos com GPT
│  ├─ .env               # Chave e configs (não versionado)
│  ├─ requirements.txt   # Dependências Python
│  └─ work/
│     ├─ cache/          # Cache (opcional)
│     └─ jobs.json       # Status de jobs (best-effort)
└─ Front/
   ├─ manifest.json      # Manifesto da extensão
   ├─ popup.html         # UI do popup
   ├─ popup.js           # Lógica (inicia job + faz polling)
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

Preferencial:
```bash
pip install -r requirements.txt
```

Ou manual:
```bash
pip install flask flask-cors openai python-dotenv yt-dlp
```

### 4. Instalar FFmpeg

**Obrigatório:** É necessário ter o executável do `ffmpeg` para segmentar/converter áudio.

1. Baixe um build do ffmpeg.
2. Adicione a pasta `bin` ao **PATH** do sistema, OU defina o caminho absoluto usando `FFMPEG_PATH` no `.env`.

### 5. Configurar variáveis de ambiente

Crie um arquivo `.env` na pasta `Back/`:
```ini
OPENAI_API_KEY=sua_chave_da_openai_aqui

# Opcional (recomendado)
FFMPEG_PATH=/caminho/para/ffmpeg

TRANSCRIBE_MODEL=gpt-4o-mini-transcribe
TRANSCRIBE_SEGMENT_SECONDS=480
TRANSCRIBE_WORKERS=1
TRANSCRIBE_MAX_RETRIES=6

MAX_JOBS=2

YTDLP_COOKIES_FROM_BROWSER=chrome
```

---

## ▶️ Executando o Backend

A partir da pasta `Back/`:

```bash
python main.py
```

* **Servidor roda em:** `http://127.0.0.1:5000`
* **Health:** `GET /health`
* **Iniciar job:** `POST /process`
* **Consultar status/resultados:** `GET /status/<job_id>`

---

## 🔌 Endpoint da API

### `POST /process` (inicia job assíncrono)

**Corpo da Requisição (JSON):**
```json
{
  "video_url": "https://www.youtube.com/watch?v=XXXX",
  "num_topicos": 7
}
```

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| `video_url` | string | URL completa do vídeo do YouTube. |
| `num_topicos` | int | (Opcional) Quantidade de tópicos a extrair. Padrão: 7. |

**Resposta (Aceito - 202):**
```json
{
  "job_id": "e9a1675f-3452-4560-afab-9f9642529740",
  "status": "queued"
}
```

### `GET /status/<job_id>` (consulta status)

**Em execução:**
```json
{
  "status": "running",
  "progress": 35,
  "step": "transcribing"
}
```

**Concluído:**
```json
{
  "status": "done",
  "progress": 100,
  "topics": "1. Tópico um\n2. Tópico dois\n3. Tópico três\n..."
}
```

**Erro:**
```json
{
  "status": "error",
  "progress": 100,
  "error": "Mensagem detalhada do erro"
}
```

---

## 🧠 Como Funciona (Pipeline)

1. **Inicia job:** `main.py` recebe `POST /process`, cria `job_id` e retorna imediatamente (HTTP 202).
2. **Download:** `transcricao.py` usa `yt-dlp` para baixar o áudio em `work/audio.<ext>` (cookies opcionais para vídeos restritos).
3. **Segmentação e Transcrição:**
   * Segmenta/converte o áudio em partes menores usando `ffmpeg`.
   * Transcreve cada segmento via OpenAI **Audio Transcriptions (speech-to-text)**.
   * Concorrência e retry/backoff são configuráveis.
4. **Extração de Tópicos:** `topicos.py` divide o texto em *chunks*, extrai tópicos candidatos e consolida o resultado numa lista final numerada.

---

## 🧩 Possíveis Melhorias

- [ ] Cache por ID do vídeo (evitar reprocessamento).
- [ ] Suporte para múltiplos idiomas de saída.
- [ ] Streaming de progresso (Download → Transcrição → Resumo) via WebSocket / SSE (em vez de polling).
- [ ] Timestamps por tópico para navegação no vídeo.
- [ ] Modo deploy (Docker + servidor WSGI em produção).
