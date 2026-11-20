
import hashlib
import json
import time
from pathlib import Path

import chromadb
import pymupdf

from app.chunking import clean_text, split_text
from app.embed import embed_texts
from app.rag import answer_question

BASE_DIR = Path(__file__).resolve().parent.parent

PDF_PATH = (
    BASE_DIR / "data" / "raw" /
    "1679997242339591060file.pdf"
)

EVAL_FILE = BASE_DIR / "eval" / "eval_set.json"

RESULT_FILE = BASE_DIR / "eval" / "config_results.json"

CHROMA_PATH = BASE_DIR / "data" / "eval_chroma"

SOURCE_URL = (
    "https://cgwb.gov.in/cgwbpnm/public/uploads/"
    "documents/1679997242339591060file.pdf"
)

DOCUMENT_TITLE = "Manual on Artificial Recharge of Ground Water"


CONFIGS = [
    {
        "name": "A",
        "chunk_size": 1200,
        "overlap": 200,
        "top_k": 3
    },
    {
        "name": "B",
        "chunk_size": 800,
        "overlap": 100,
        "top_k": 5
    }
]


def load_chunks(chunk_size, overlap):

    chunks = []

    with pymupdf.open(PDF_PATH) as pdf:

        for page_number, page in enumerate(pdf, start=1):

            text = clean_text(page.get_text("text"))

            if not text:
                continue

            page_chunks = split_text(
                text,
                chunk_size=chunk_size,
                overlap=overlap
            )

            for chunk_number, chunk in enumerate(
                page_chunks, start=1
            ):

                chunks.append({
                    "text": chunk,
                    "metadata": {
                        "title": DOCUMENT_TITLE,
                        "source": SOURCE_URL,
                        "page": page_number,
                        "chunk": chunk_number
                    }
                })

    return chunks


def build_collection(client, chunks, name):

    collection = client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )

    batch_size = 16

    for start in range(0, len(chunks), batch_size):

        batch = chunks[start:start + batch_size]

        ids = [
            hashlib.sha256(
                (
                    str(item["metadata"]["page"])
                    + str(item["metadata"]["chunk"])
                    + item["text"]
                ).encode("utf-8")
            ).hexdigest()
            for item in batch
        ]

        # Find chunks already stored.
        existing_ids = set(
            collection.get(ids=ids)["ids"]
        )

        new_items = [
            item
            for item, item_id in zip(batch, ids)
            if item_id not in existing_ids
        ]

        new_ids = [
            item_id
            for item_id in ids
            if item_id not in existing_ids
        ]

        if not new_items:

            print(
                f"Already indexed through chunk "
                f"{start + len(batch)}/{len(chunks)}"
            )

            continue

        documents = [
            item["text"] for item in new_items
        ]

        metadatas = [
            item["metadata"] for item in new_items
        ]

        # Retry temporary embedding/network failures.
        for attempt in range(1, 5):

            try:

                embeddings = embed_texts(documents)
                break

            except Exception as error:

                if attempt == 4:
                    raise

                wait_time = attempt * 15

                print("Embedding failed:", error)

                print(
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

        collection.upsert(
            ids=new_ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

        print(
            f"Indexed {start + len(batch)}/{len(chunks)} chunks"
        )

        time.sleep(12)

    return collection


def evaluate_config(client, config, questions, query_vectors):

    print(
        f"\nEvaluating Configuration {config['name']}"
    )

    chunks = load_chunks(
        config["chunk_size"],
        config["overlap"]
    )

    print("Total chunks:", len(chunks))

    collection = build_collection(
        client,
        chunks,
        "eval_config_" + config["name"].lower()
    )

    # Retrieve results only for answerable questions.
    answerable_questions = [
        item for item in questions
        if not item["must_abstain"]
    ]

    results = collection.query(
        query_embeddings=query_vectors,
        n_results=config["top_k"],
        include=["documents"]
    )

    total_coverage = 0
    evaluated = 0

    for index, question in enumerate(answerable_questions):

        retrieved_documents = (
            results["documents"][index] or []
        )

        retrieved_text = " ".join(
            retrieved_documents
        ).lower()

        keywords = question["expected_keywords"]

        matched = sum(
            1
            for keyword in keywords
            if keyword.lower() in retrieved_text
        )

        coverage = (
            matched / len(keywords)
            if keywords else 0
        )

        total_coverage += coverage
        evaluated += 1

    keyword_coverage = (
        total_coverage / evaluated * 100
        if evaluated else 0
    )

    # Check Q6: unsupported plot-level groundwater data.
    q6 = next(
        item for item in questions
        if item["must_abstain"]
    )

    q6_result = answer_question(
        q6["question"]
    )

    abstention_pass = (
        q6_result["answer"].strip().lower()
        == "i don't know."
    )

    return {
        "name": config["name"],
        "chunk_size": config["chunk_size"],
        "overlap": config["overlap"],
        "top_k": config["top_k"],
        "total_chunks": len(chunks),
        "keyword_coverage": round(
            keyword_coverage, 2
        ),
        "q6_abstention": abstention_pass
    }


def main():

    if not PDF_PATH.exists():

        raise FileNotFoundError(
            f"PDF not found: {PDF_PATH}"
        )

    if not EVAL_FILE.exists():

        raise FileNotFoundError(
            f"Evaluation file not found: {EVAL_FILE}"
        )

    with open(EVAL_FILE, "r", encoding="utf-8") as file:

        questions = json.load(file)

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    answerable_questions = [
        item for item in questions
        if not item["must_abstain"]
    ]

    query_texts = [
        item["question"]
        for item in answerable_questions
    ]

    print(
        "Generating evaluation query embeddings..."
    )

    query_vectors = embed_texts(query_texts)

    all_results = []

    for config in CONFIGS:

        result = evaluate_config(
            client,
            config,
            questions,
            query_vectors
        )

        all_results.append(result)

    # Select the best configuration.
    # Q6 must pass; then keyword coverage decides.
    valid_results = [
        item for item in all_results
        if item["q6_abstention"]
    ]

    if valid_results:

        winner = max(
            valid_results,
            key=lambda item: item["keyword_coverage"]
        )

    else:

        winner = None

    print(
        "\n========== EVALUATION RESULTS =========="
    )

    print(
        f"{'Config':<10}"
        f"{'Chunk':<10}"
        f"{'Top-k':<10}"
        f"{'Coverage':<15}"
        f"{'Q6 Pass'}"
    )

    for result in all_results:

        print(
            f"{result['name']:<10}"
            f"{result['chunk_size']:<10}"
            f"{result['top_k']:<10}"
            f"{result['keyword_coverage']}%"
            f"{'':<10}"
            f"{result['q6_abstention']}"
        )

    if winner:

        print(
            "\nWINNER: Configuration",
            winner["name"]
        )

    else:

        print(
            "\nNo winning configuration: "
            "Q6 abstention failed."
        )

    output = {
        "evaluation_questions": len(questions),
        "answerable_questions": len(answerable_questions),
        "winner": winner["name"] if winner else None,
        "results": all_results
    }

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4
        )

    print(
        "\nResults saved to:",
        RESULT_FILE
    )


if __name__ == "__main__":

    main()
