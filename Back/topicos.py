import openai
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar a API do OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def extract_topics_with_gpt(transcription, num_topicos):
    """Usa a API do OpenAI GPT para gerar os principais tópicos."""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Novo formato de cliente

        prompt = f"""
        Extraia os {num_topicos} principais tópicos abordados na seguinte transcrição e retorne uma lista clara e concisa:

        {transcription}
        """

        response = client.chat.completions.create(
            model="gpt-4",  # Use "gpt-3.5-turbo" se quiser um modelo mais barato
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em resumir conteúdos educativos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7  # Ajuste para controlar a criatividade da resposta
        )

        return response.choices[0].message.content.strip() if response.choices else None

    except Exception as e:
        print(f"Erro ao processar os tópicos com OpenAI GPT: {e}")
        return None
