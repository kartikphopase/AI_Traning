
import re
from pathlib import Path

import fitz

BASE_DIR = Path(__file__).resolve().parent.parent

PDF_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "1679997242339591060file.pdf"
)

SOURCE_URL = (
    "https://cgwb.gov.in/cgwbpnm/public/uploads/"
    "documents/1679997242339591060file.pdf"
)

DOCUMENT_TITLE = "Manual on Artificial Recharge of Ground Water"


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_text(text, chunk_size=1200, overlap=200):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def load_pdf_chunks():

    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"CGWB PDF not found: {PDF_PATH}"
        )

    all_chunks = []

    with fitz.open(PDF_PATH) as pdf:

        for page_number, page in enumerate(pdf, start=1):

            text = clean_text(page.get_text("text"))

            if not text:
                continue

            page_chunks = split_text(text)

            for chunk_number, chunk in enumerate(
                page_chunks,
                start=1
            ):

                all_chunks.append({
                    "text": chunk,
                    "metadata": {
                        "title": DOCUMENT_TITLE,
                        "source": SOURCE_URL,
                        "page": page_number,
                        "chunk": chunk_number
                    }
                })

    return all_chunks


if __name__ == "__main__":

    chunks = load_pdf_chunks()

    print("CHUNKING COMPLETED")
    print("Total chunks:", len(chunks))

    if chunks:
        print("\nFirst chunk:")
        print(chunks[0]["text"][:300])

        print("\nMetadata:")
        print(chunks[0]["metadata"])
