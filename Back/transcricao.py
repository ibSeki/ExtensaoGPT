import subprocess
import requests

from dotenv import load_dotenv
import os
load_dotenv()

# Configure sua chave da API AssemblyAI
ASSEMBLYAI_API_KEY = os.getenv("API_KEY_TRANSCRICAO")
ASSEMBLYAI_API_URL = "https://api.assemblyai.com/v2"

headers_assemblyai = {
    "authorization": ASSEMBLYAI_API_KEY,
    "content-type": "application/json"
}

def download_audio_from_youtube(video_url):
    """Baixa o áudio de um vídeo do YouTube e converte para MP3."""
    try:
        output_path = "audio.mp3"
        command = f'yt-dlp --extract-audio --audio-format mp3 -o "{output_path}" "{video_url}"'

        # Execute o comando e capture saída e erro
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Print para debug
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        if result.returncode == 0:
            print("Áudio baixado com sucesso!")
            return output_path
        else:
            print("Erro ao baixar o áudio:", result.stderr)
            return None

    except Exception as e:
        print(f"Erro ao executar yt-dlp: {e}")
        return None


def upload_audio(file_path):
    """Faz upload do arquivo de áudio para a API da AssemblyAI e retorna a URL do arquivo."""
    try:
        with open(file_path, "rb") as audio_file:
            response = requests.post(
                f"{ASSEMBLYAI_API_URL}/upload",
                headers={"authorization": ASSEMBLYAI_API_KEY},
                files={"file": audio_file}
            )
            response.raise_for_status()
            print("Áudio enviado com sucesso!")
            return response.json()["upload_url"]
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer upload do áudio: {e}")
        return None

def transcribe_audio(audio_url, language_code):
    """Solicita a transcrição do áudio na API da AssemblyAI."""
    try:
        payload = {"audio_url": audio_url, "language_code": language_code}
        response = requests.post(f"{ASSEMBLYAI_API_URL}/transcript", json=payload, headers=headers_assemblyai)
        response.raise_for_status()
        transcript_id = response.json()["id"]

        print("Aguardando a transcrição ser concluída...")
        while True:
            status_response = requests.get(f"{ASSEMBLYAI_API_URL}/transcript/{transcript_id}", headers=headers_assemblyai)
            status_response.raise_for_status()
            status_data = status_response.json()

            if status_data["status"] == "completed":
                print("Transcrição concluída com sucesso!")
                return status_data["text"]
            elif status_data["status"] == "failed":
                print(f"Erro na transcrição: {status_data['error']}")
                return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao solicitar a transcrição: {e}")
        return None

def delete_audio_file(file_path):
    """Exclui o arquivo de áudio após a execução."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Arquivo de áudio {file_path} excluído com sucesso!")
        else:
            print(f"O arquivo {file_path} não foi encontrado.")
    except Exception as e:
        print(f"Erro ao excluir o arquivo de áudio: {e}")
