
import os

from pathlib import Path
from dotenv import load_dotenv, dotenv_values
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

MODEL_NAME = "gemini-embedding-001"


def get_client():

    load_dotenv(ENV_FILE, override=True)

    env_values = dotenv_values(ENV_FILE)

    api_key = (
        os.getenv("GEMINI_API_KEY")
        or env_values.get("GEMINI_API_KEY")
    )

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing in .env"
        )

    return genai.Client(api_key=api_key)


def embed_texts(texts):

    if not texts:
        return []

    client = get_client()

    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=texts
    )

    return [
        embedding.values
        for embedding in response.embeddings
    ]


if __name__ == "__main__":

    test_text = [
        "Rooftop rainwater harvesting collects rainwater."
    ]

    vectors = embed_texts(test_text)

    print("EMBEDDING TEST SUCCESSFUL")
    print("Number of vectors:", len(vectors))
    print("Vector dimensions:", len(vectors[0]))
