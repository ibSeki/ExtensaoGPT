from flask import Flask, request, jsonify
from flask_cors import CORS
from transcricao import download_audio_from_youtube, transcribe_audio, delete_audio_file
from topicos import extract_topics_with_gpt
from dotenv import load_dotenv
import os

load_dotenv()

print("Key loaded:", os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app)

@app.route("/process", methods=["POST"])
def process_video():
    data = request.get_json() or {}

    video_url = (data.get("video_url") or "").strip()
    num_topics_raw = data.get("num_topicos", 7)  # pode vir int ou string

    # 🔹 garante que vira inteiro
    try:
        num_topics = int(num_topics_raw)
    except (TypeError, ValueError):
        num_topics = 7

    print(f"[DEBUG] video_url recebido: {video_url}")
    print(f"[DEBUG] num_topicos recebido: {num_topics_raw} -> usando: {num_topics}")

    if not video_url:
        return jsonify({"error": "Video URL not provided."}), 400

    # 1) baixa o áudio
    audio_file = download_audio_from_youtube(video_url)
    if not audio_file:
        return jsonify({"error": "Error downloading the video audio."}), 500

    # 2) transcreve
    transcription = transcribe_audio(audio_file)
    if not transcription:
        delete_audio_file(audio_file)
        return jsonify({"error": "Error transcribing the audio."}), 500

    # 3) extrai tópicos (usa num_topics escolhido no popup)
    topics = extract_topics_with_gpt(transcription, num_topics)
    delete_audio_file(audio_file)

    if not topics:
        return jsonify({"error": "Error processing the topics."}), 500

    return jsonify({"topics": topics}), 200


if __name__ == "__main__":
    # mantém porta 5000 pra bater com o fetch do popup
    app.run(debug=True)
