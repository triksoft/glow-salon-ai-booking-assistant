from google import genai
from config.config import get_gemini_api_key


EMBEDDING_MODEL = "gemini-embedding-001"


client = genai.Client(
    api_key=get_gemini_api_key()
)


def create_embedding(text):
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[text]
    )

    return response.embeddings[0].values