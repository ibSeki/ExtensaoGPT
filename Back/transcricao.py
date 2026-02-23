import openai
import os
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔹 Caminho COMPLETO do ffmpeg.exe (usei o que você enviou)
FFMPEG_PATH = r"C:\Users\IandeBarrosSeki-Date\OneDrive - COMPANHIA DPASCHOAL DE PARTICIPACOES\Documentos\ffmpeg-2025-11-24-git-c732564d2e-essentials_build\bin\ffmpeg.exe"


def _ensure_ffmpeg():
    """Verifica se o ffmpeg existe no caminho configurado."""
    if not os.path.exists(FFMPEG_PATH):
        raise FileNotFoundError(
            f"FFmpeg não encontrado em: {FFMPEG_PATH}. "
            "Verifique o caminho em transcricao.py (FFMPEG_PATH)."
        )


def download_audio_from_youtube(video_url):
    """
    Baixa só o áudio no melhor formato disponível, sem reencodar.
    Mais rápido que converter diretamente para mp3.
    """
    try:
        out_dir = Path("work")
        out_dir.mkdir(exist_ok=True)

        output_tmpl = str(out_dir / "audio.%(ext)s")

        command = [
            "yt-dlp",
            "-f", "bestaudio/best",
            "--no-playlist",
            "-o", output_tmpl,
            video_url
        ]

        subprocess.run(command, check=True)

        # Encontra o arquivo baixado mais recente
        audio_file = max(out_dir.glob("audio.*"), key=lambda p: p.stat().st_mtime)
        print("🔹 Audio successfully downloaded!")
        return str(audio_file)

    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading audio: {e}")
        return None


def _split_audio_ffmpeg(file_path: str, segment_seconds: int = 8 * 60):
    """
    Divide o áudio em segmentos menores para transcrever mais rápido.
    Usa o caminho completo do ffmpeg.exe.
    """
    _ensure_ffmpeg()

    file_path = Path(file_path)
    seg_dir = file_path.parent / "segments"
    seg_dir.mkdir(exist_ok=True)

    # tenta split sem reencodar (mais rápido)
    seg_tmpl_copy = str(seg_dir / ("seg_%03d" + file_path.suffix))
    cmd_copy = [
        FFMPEG_PATH, "-hide_banner", "-loglevel", "error",
        "-i", str(file_path),
        "-f", "segment",
        "-segment_time", str(segment_seconds),
        "-reset_timestamps", "1",
        "-c", "copy",
        seg_tmpl_copy
    ]

    try:
        subprocess.run(cmd_copy, check=True)
        segments = sorted(seg_dir.glob("seg_*" + file_path.suffix))
        if segments:
            return [str(p) for p in segments]
    except subprocess.CalledProcessError:
        pass

    # fallback: reencoda para mp3 leve
    seg_tmpl_mp3 = str(seg_dir / "seg_%03d.mp3")
    cmd_mp3 = [
        FFMPEG_PATH, "-hide_banner", "-loglevel", "error",
        "-i", str(file_path),
        "-f", "segment",
        "-segment_time", str(segment_seconds),
        "-reset_timestamps", "1",
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-codec:a", "mp3",
        "-q:a", "4",
        seg_tmpl_mp3
    ]
    subprocess.run(cmd_mp3, check=True)
    segments = sorted(seg_dir.glob("seg_*.mp3"))
    return [str(p) for p in segments]


def _transcribe_one_segment(client, seg_path: str):
    with open(seg_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return response.text


def transcribe_audio(file_path, segment_seconds=8 * 60, workers=3):
    """
    Transcreve usando Whisper-1:
    - divide em segmentos se necessário
    - transcreve segmentos em paralelo (mais rápido para vídeos longos)
    """
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        segments = _split_audio_ffmpeg(file_path, segment_seconds=segment_seconds)

        # se for um segmento só, transcreve direto
        if len(segments) == 1:
            print("✅ Transcription started (single segment)...")
            return _transcribe_one_segment(client, segments[0])

        print(f"✅ Transcribing {len(segments)} segments in parallel...")

        texts = [None] * len(segments)
        with ThreadPoolExecutor(max_workers=workers) as ex:
            fut_map = {
                ex.submit(_transcribe_one_segment, client, p): i
                for i, p in enumerate(segments)
            }
            for fut in as_completed(fut_map):
                i = fut_map[fut]
                texts[i] = fut.result()

        print("✅ Transcription completed successfully!")
        return "\n".join(texts)

    except Exception as e:
        print(f"❌ Error transcribing audio: {e}")
        return None


def delete_audio_file(file_path):
    """
    Deleta o áudio original e também os segmentos temporários.
    """
    try:
        p = Path(file_path)
        if p.exists():
            p.unlink()

        seg_dir = p.parent / "segments"
        if seg_dir.exists():
            for f in seg_dir.glob("*"):
                f.unlink()
            seg_dir.rmdir()

        print(f"🗑 Audio file {file_path} and segments successfully deleted!")
    except Exception as e:
        print(f"❌ Error deleting audio file: {e}")
