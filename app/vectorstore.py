
import hashlib
import time

import chromadb

from app.chunking import load_pdf_chunks
from app.embed import embed_texts, embed_texts_local

BASE_DIR = __import__("pathlib").Path(__file__).resolve().parent.parent

CHROMA_DIR = BASE_DIR / "data" / "chroma"

COLLECTION_NAME = "jalsanchay_cgwb"
LOCAL_COLLECTION_NAME = "jalsanchay_cgwb_local"
CONFIG_COLLECTION_NAME = "jalsanchay_config"


def get_client():
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_config_collection():
    return get_client().get_or_create_collection(
        name=CONFIG_COLLECTION_NAME,
        metadata={"active_provider": "gemini"}
    )


def get_active_provider():
    config = get_config_collection()
    return (config.metadata or {}).get(
        "active_provider", "gemini"
    )


def set_active_provider(provider):
    config = get_config_collection()
    config.modify(metadata={"active_provider": provider})
    print(f"Active embedding provider: {provider}")


def get_collection(provider=None):
    if provider is None:
        provider = get_active_provider()

    name = (
        LOCAL_COLLECTION_NAME
        if provider == "local"
        else COLLECTION_NAME
    )

    return get_client().get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )


def is_quota_error(error):
    message = str(error).lower()

    return any(term in message for term in [
        "429",
        "resource_exhausted",
        "quota exceeded",
        "rate limit"
    ])


def generate_embeddings(texts, provider):
    if provider == "local":
        return embed_texts_local(texts)

    return embed_texts(texts)


def build_index(provider=None):
    if provider is None:
        provider = get_active_provider()

    print("Reading CGWB PDF...")

    chunks = load_pdf_chunks()

    if not chunks:
        raise ValueError("No PDF chunks found")

    collection = get_collection(provider)

    print("Embedding provider:", provider)
    print("Total chunks:", len(chunks))
    print("Already indexed:", collection.count())

    batch_size = 16 if provider == "gemini" else 64

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]

        documents = [item["text"] for item in batch]
        metadatas = [item["metadata"] for item in batch]

        try:
            embeddings = generate_embeddings(
                documents, provider
            )
        except Exception as error:
            if provider == "gemini" and is_quota_error(error):
                print(
                    "Gemini quota exhausted. "
                    "Switching to local embeddings..."
                )
                return build_index(provider="local")

            raise

        ids = []

        for item in batch:
            identity = (
                str(item["metadata"]["page"])
                + str(item["metadata"]["chunk"])
                + item["text"]
            )

            ids.append(
                hashlib.sha256(
                    identity.encode("utf-8")
                ).hexdigest()
            )

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

        completed = min(start + batch_size, len(chunks))

        print(f"Indexed {completed}/{len(chunks)} chunks")

        if provider == "gemini" and completed < len(chunks):
            time.sleep(12)

    if collection.count() < len(chunks):
        raise RuntimeError("Indexing incomplete")

    set_active_provider(provider)

    print("\nVECTOR INDEX COMPLETED")
    print("Embedding provider:", provider)
    print("Total indexed chunks:", collection.count())

    return collection.count()


def semantic_search(query, limit=5):
    if not query.strip():
        raise ValueError("Search query cannot be empty")

    provider = get_active_provider()
    collection = get_collection(provider)

    total = collection.count()

    if total == 0:
        raise RuntimeError(
            "Vector database is empty. "
            "Run python -m app.vectorstore first."
        )

    try:
        query_embedding = generate_embeddings(
            [query], provider
        )[0]

    except Exception as error:
        if provider == "gemini" and is_quota_error(error):
            print(
                "Gemini query quota exhausted. "
                "Building local index..."
            )

            build_index(provider="local")

            provider = "local"
            collection = get_collection(provider)

            query_embedding = embed_texts_local([query])[0]
        else:
            raise

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(limit, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    output = []

    for index in range(len(results["ids"][0])):
        output.append({
            "text": results["documents"][0][index],
            "metadata": results["metadatas"][0][index],
            "distance": results["distances"][0][index]
        })

    return output


if __name__ == "__main__":
    build_index()
