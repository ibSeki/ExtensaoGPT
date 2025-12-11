import openai
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Prompt base EXATO que você pediu
BASE_PROMPT = (
    "Generate a concise summary by extracting the X most im- portant topics from the following text. "
    "Focus on highlighting important information that encapsulates the main points of the content."
)


def _chunk_text(text: str, max_chars: int = 12000):
    """
    Divide a transcrição em blocos menores para evitar mandar tudo de uma vez
    (menos tokens => resposta mais rápida).
    """
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, buf = [], ""

    for p in paragraphs:
        if len(buf) + len(p) + 1 > max_chars:
            if buf:
                chunks.append(buf)
                buf = ""
        buf += p + "\n"

    if buf:
        chunks.append(buf)

    return chunks


def _topics_for_chunk(client, chunk: str, k: int):
    """
    Extrai tópicos de um pedaço da transcrição usando GPT-4
    com o prompt EXATO (substituindo X por k).
    """
    prompt = BASE_PROMPT.replace("X", str(k)) + f"\n\n{chunk}"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant specialized in summarizing educational content."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=220
    )

    raw = response.choices[0].message.content.strip()

    # Tenta quebrar em linhas/tópicos de forma robusta
    lines = re.split(r"\n+|•\s*|-+\s*|\d+\.\s*", raw)
    topics = [l.strip(" -•\t") for l in lines if l.strip()]
    return topics[:k]


def extract_topics_with_gpt(transcription, num_topicos, workers=2):
    """
    Usa GPT-4 para gerar tópicos principais de forma mais rápida:
    1) divide a transcrição em chunks
    2) extrai tópicos por chunk (paralelo leve)
    3) consolida os melhores tópicos finais

    Respeita SEMPRE o prompt:
    "Generate a concise summary by extracting the X most im- portant topics from the following text..."
    """
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        chunks = _chunk_text(transcription, max_chars=12000)

        # Se for curto, faz direto em uma chamada
        if len(chunks) == 1:
            prompt = BASE_PROMPT.replace("X", str(num_topicos)) + f"\n\n{transcription}"

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant specialized in summarizing educational content."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=320
            )
            return response.choices[0].message.content.strip() if response.choices else None

        # 1) candidatos por chunk (paralelo conservador)
        candidates = []
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_topics_for_chunk, client, c, num_topicos) for c in chunks]
            for fut in as_completed(futs):
                candidates.extend(fut.result())

        # remove duplicados simples
        seen, unique = set(), []
        for t in candidates:
            key = t.lower()
            if key not in seen:
                seen.add(key)
                unique.append(t)

        # 2) consolidação final usando o MESMO prompt base
        candidates_text = "\n".join(f"- {t}" for t in unique)
        merge_prompt = BASE_PROMPT.replace("X", str(num_topicos)) + f"\n\n{candidates_text}"

        final_resp = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant specialized in summarizing educational content."
                },
                {"role": "user", "content": merge_prompt}
            ],
            temperature=0.2,
            max_tokens=320
        )

        return final_resp.choices[0].message.content.strip() if final_resp.choices else None

    except Exception as e:
        print(f"Error processing topics with OpenAI GPT: {e}")
        return None
