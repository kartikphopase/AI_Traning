import json
import fitz
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "data" / "raw" / "1679997242339591060file.pdf"
OUTPUT_PATH = BASE_DIR / "data" / "records.json"


from data.sample_records import records

SOURCE_URL = "https://cgwb.gov.in/cgwbpnm/public/uploads/documents/1679997242339591060file.pdf"

FIELDS = [
    "topic",
    "document",
    "section",
    "rule_or_value",
    "unit",
    "source_url"
]


def clean_record(row):
    try:
        cleaned = {}

        for field in FIELDS:
            value = str(row.get(field, "")).strip()

            if not value:
                raise ValueError(f"Missing field: {field}")

            cleaned[field] = value

        cleaned["source_url"] = SOURCE_URL
        return cleaned

    except (AttributeError, TypeError, ValueError) as error:
        print("Skipping bad record:", error)
        return None


def main():
    try:
        
        if not PDF_PATH.exists():
            raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

        with fitz.open(PDF_PATH) as pdf:
            pdf_text = "".join(page.get_text() for page in pdf)
            print("PDF pages:", len(pdf))
            print("Extracted characters:", len(pdf_text))

        if not pdf_text.strip():
            raise ValueError("No readable text found in PDF")

        
        cleaned_records = []

        for row in records:
            cleaned = clean_record(row)

            if cleaned:
                cleaned_records.append(cleaned)

        
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
            json.dump(cleaned_records, file, indent=4, ensure_ascii=False)

        print("Successfully saved records!")
        print("Total records:", len(cleaned_records))
        print("Output:", OUTPUT_PATH)

    except Exception as error:
        print("Ingestion error:", error)


if __name__ == "__main__":
    main()
