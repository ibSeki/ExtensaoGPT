import openai
import os
import subprocess
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar a API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def download_audio_from_youtube(video_url):
    """Baixa o áudio de um vídeo do YouTube e converte para MP3."""
    try:
        output_path = "audio.mp3"

        # Baixar e converter o áudio usando yt-dlp
        command = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "-o", output_path,
            video_url
        ]

        subprocess.run(command, check=True)
        print("🔹 Áudio baixado e convertido para MP3 com sucesso!")
        return output_path

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao baixar ou converter o áudio: {e}")
        return None

def transcribe_audio(file_path):
    """Faz a transcrição do áudio usando a API Whisper da OpenAI, sem precisar de idioma."""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Criar cliente da OpenAI

        with open(file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file  # Remove `language`
            )

        print("✅ Transcrição concluída com sucesso!")
        return response.text  # Retorna o texto transcrito

    except Exception as e:
        print(f"❌ Erro ao transcrever o áudio: {e}")
        return None

def delete_audio_file(file_path):
    """Exclui o arquivo de áudio após a execução."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑 Arquivo de áudio {file_path} excluído com sucesso!")
        else:
            print(f"⚠ O arquivo {file_path} não foi encontrado.")
    except Exception as e:
        print(f"❌ Erro ao excluir o arquivo de áudio: {e}")
