
import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv
from google import genai
from sklearn.feature_extraction.text import HashingVectorizer

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

MODEL_NAME = "gemini-embedding-001"
LOCAL_VECTOR_SIZE = 3072

# Stateless local fallback: same text always produces the same vector.
local_vectorizer = HashingVectorizer(
    n_features=LOCAL_VECTOR_SIZE,
    alternate_sign=False,
    norm="l2",
    ngram_range=(1, 2),
)


def get_client():
    load_dotenv(ENV_FILE, override=True)
    env_values = dotenv_values(ENV_FILE)

    api_key = (
        os.getenv("GEMINI_API_KEY")
        or env_values.get("GEMINI_API_KEY")
    )

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing in .env")

    return genai.Client(api_key=api_key)


def embed_texts_gemini(texts):
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


def embed_texts_local(texts):
    if not texts:
        return []

    vectors = local_vectorizer.transform(texts)
    return vectors.toarray().tolist()


def embed_texts(texts):
    """Keep Gemini as the existing primary embedding provider."""
    return embed_texts_gemini(texts)


if __name__ == "__main__":
    test_text = [
        "Rooftop rainwater harvesting collects rainwater."
    ]

    vectors = embed_texts_local(test_text)

    print("LOCAL EMBEDDING TEST SUCCESSFUL")
    print("Number of vectors:", len(vectors))
    print("Vector dimensions:", len(vectors[0]))
