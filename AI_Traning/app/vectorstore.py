
import hashlib
import time
import chromadb

from pathlib import Path

from app.chunking import load_pdf_chunks
from app.embed import embed_texts


BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = BASE_DIR / "data" / "chroma"

COLLECTION_NAME = "jalsanchay_cgwb"


def get_collection():

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    return collection


def build_index():

    print("Reading CGWB PDF...")

    chunks = load_pdf_chunks()

    if not chunks:
        raise ValueError("No PDF chunks found")

    collection = get_collection()

    print("Total chunks:", len(chunks))
    print("Already indexed:", collection.count())
    print("Generating embeddings...")

    # Smaller batches help reduce API quota pressure.
    batch_size = 16

    for start in range(0, len(chunks), batch_size):

        batch = chunks[start:start + batch_size]

        documents = [
            item["text"] for item in batch
        ]

        metadatas = [
            item["metadata"] for item in batch
        ]

        # Generate embeddings for the current batch.
        embeddings = embed_texts(documents)

        ids = []

        for item in batch:

            identity = (
                str(item["metadata"]["page"])
                + str(item["metadata"]["chunk"])
                + item["text"]
            )

            chunk_id = hashlib.sha256(
                identity.encode("utf-8")
            ).hexdigest()

            ids.append(chunk_id)

        # Upsert prevents duplicate IDs when restarting.
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

        completed = min(
            start + batch_size,
            len(chunks)
        )

        print(
            f"Indexed {completed}/{len(chunks)} chunks"
        )

        # Wait before sending the next API request.
        if completed < len(chunks):
            time.sleep(12)

    print("\nVECTOR INDEX COMPLETED")
    print("Total indexed chunks:", collection.count())

    return collection.count()


def semantic_search(query, limit=5):

    if not query.strip():
        raise ValueError("Search query cannot be empty")

    collection = get_collection()

    total = collection.count()

    if total == 0:
        raise RuntimeError(
            "Vector database is empty. "
            "Run python -m app.vectorstore first."
        )

    # Generate embedding for the user's search query.
    query_embedding = embed_texts([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(limit, total),
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
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
