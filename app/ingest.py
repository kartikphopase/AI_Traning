
import json
import re
from pathlib import Path

import fitz

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "data" / "raw" / "1679997242339591060file.pdf"
OUTPUT_PATH = BASE_DIR / "data" / "records.json"

SOURCE_URL = (
    "https://cgwb.gov.in/cgwbpnm/public/uploads/"
    "documents/1679997242339591060file.pdf"
)

DOCUMENT = "Manual on Artificial Recharge of Ground Water"


def add_record(records, topic, section, value, unit):
    records.append({
        "topic": topic,
        "document": DOCUMENT,
        "section": section,
        "rule_or_value": value.strip(),
        "unit": unit,
        "source_url": SOURCE_URL
    })


def extract_records(text):
    records = []

    # 1. Roof runoff coefficients
    roof_patterns = [
        (r"GI\s*Sheet\s*[\r\n ]+0\.9", "GI Sheet", "0.9"),
        (r"Asbestos\s*[\r\n ]+0\.8", "Asbestos", "0.8"),
        (r"Tiled\s*[\r\n ]+0\.75", "Tiled roof", "0.75"),
        (r"Concrete\s*[\r\n ]+0\.7", "Concrete roof", "0.7")
    ]

    for pattern, material, value in roof_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            add_record(
                records,
                "Roof runoff coefficient",
                "7.2.7 - Table 7.2",
                f"{material}: {value}",
                "coefficient"
            )

    # 2. Storage tank capacities
    tank_patterns = [
        (
            r"ferro[-\s]*cement.*?4,000\s*(?:and|to|-)\s*15,000\s*L",
            "Ferro-cement tanks: 4,000 to 15,000 litres"
        ),
        (
            r"15,000\s*to\s*50,000\s*L",
            "Brick, stone or cement brick tanks: 15,000 to 50,000 litres"
        ),
        (
            r"exceeding\s*50,000\s*L",
            "Concrete and RCC tanks: capacities exceeding 50,000 litres"
        )
    ]

    for pattern, value in tank_patterns:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            add_record(
                records,
                "Storage tank capacity",
                "7.2.7 - Storage Tank",
                value,
                "litres"
            )

    # 3. Water scarcity period
    match = re.search(
        r"range of\s*(90\s*days\s*to\s*200\s*days)",
        text,
        re.IGNORECASE
    )

    if match:
        add_record(
            records,
            "Water scarcity period",
            "7.2.7.1 - Rural Storage Tanks",
            match.group(1),
            "days"
        )

    # 4. Per capita water requirement
    match = re.search(
        r"requirement of\s*(6\s*litres per day)",
        text,
        re.IGNORECASE
    )

    if match:
        add_record(
            records,
            "Per capita water requirement",
            "7.2.7.1 - Rural Storage Tanks",
            match.group(1),
            "litres/person/day"
        )

    # 5. Additional water requirement
    if re.search(r"Adding\s*20%", text, re.IGNORECASE):
        add_record(
            records,
            "Additional water requirement",
            "7.2.7.1 - Rural Storage Tanks",
            "Add 20% for visitors, festivals and wastage",
            "percentage"
        )

    # 6. Storage tank sizing formula
    if re.search(
        r"No\.\s*of persons.*?Period of water scarcity.*?Per capita",
        text,
        re.IGNORECASE | re.DOTALL
    ):
        add_record(
            records,
            "Storage tank sizing formula",
            "7.2.7.1 - Rural Storage Tanks",
            "Household members x scarcity days x per capita water requirement",
            "litres"
        )

    # 7. Rainwater harvesting formula
    if re.search(
        r"Annual rainfall.*?Roof area.*?Runoff Coefficient",
        text,
        re.IGNORECASE | re.DOTALL
    ):
        add_record(
            records,
            "Rainwater harvesting formula",
            "7.2.7 - Storage Tank",
            "Annual rainfall x roof area x runoff coefficient",
            "litres"
        )

    # 8. Collection sump dimensions
    match = re.search(
        r"60\s*cm\s*x\s*60\s*cm\s*x\s*60\s*cm",
        text,
        re.IGNORECASE
    )

    if match:
        add_record(
            records,
            "Collection sump dimensions",
            "7.2.8 - Collection Sump",
            match.group(0),
            "cm"
        )

    # 9. Water filtration
    if re.search(
        r"removal of suspended and colloidal impurities",
        text,
        re.IGNORECASE
    ):
        add_record(
            records,
            "Water filtration",
            "7.2.6.1 - Process of Filtration",
            "Filter media such as sand removes suspended and colloidal impurities",
            "description"
        )

    # 10. Filter media
    if re.search(
        r"coarse sand,\s*charcoal,\s*coconut fiber,\s*pebbles",
        text,
        re.IGNORECASE
    ):
        add_record(
            records,
            "Filter media",
            "7.2.6 - Filtration of Water",
            "Coarse sand, charcoal, coconut fiber, pebbles and gravels",
            "materials"
        )

    # 11. Rainwater collection example
    match = re.search(
        r"1000\s*[xX]\s*20\s*[xX]\s*0\.75\s*=\s*15,?000\s*liters",
        text,
        re.IGNORECASE
    )

    if match:
        add_record(
            records,
            "Rainwater collection example",
            "7.2.7 - Storage Tank",
            "1000 mm rainfall x 20 sq.m roof x 0.75 coefficient = 15,000 litres",
            "litres"
        )

    return records


def main():
    try:
        if not PDF_PATH.exists():
            raise FileNotFoundError(
                f"CGWB PDF not found: {PDF_PATH}"
            )

        print("Reading CGWB manual...")

        with fitz.open(PDF_PATH) as pdf:
            page_count = len(pdf)

            full_text = "\n".join(
                page.get_text() for page in pdf
            )

        if not full_text.strip():
            raise ValueError("No readable text found in PDF")

        # Find the actual Chapter 7 heading
        chapter_start = full_text.lower().rfind(
            "7. roof top rainwater harvesting"
        )

        if chapter_start == -1:
            raise ValueError("Chapter 7 not found in the PDF")

        chapter_text = full_text[chapter_start:]

        extracted_records = extract_records(chapter_text)

        if not extracted_records:
            raise ValueError("No technical records could be extracted")

        OUTPUT_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            OUTPUT_PATH,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                extracted_records,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("\nCGWB INGESTION COMPLETED")
        print("PDF pages:", page_count)
        print("Extracted records:", len(extracted_records))
        print("Saved to:", OUTPUT_PATH)

    except Exception as error:  # noqa: BLE001
        print("Ingestion error:", error)


if __name__ == "__main__":
    main()

