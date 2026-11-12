import truststore
truststore.inject_into_ssl()
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

DOCUMENTS = {
    "artificial_recharge.pdf":
        "https://cgwb.gov.in/cgwbpnm/public/uploads/documents/1679997242339591060file.pdf",

    "cgwb_publications.pdf":
        "https://cgwb.gov.in/cgwbpnm/publications?cat_id=",

    "cgwb_website.html":
        "https://cgwb.gov.in/"
}


def download_documents():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for filename, url in DOCUMENTS.items():
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            file_path = RAW_DIR / filename
            file_path.write_bytes(response.content)

            print(f"Downloaded: {filename}")

        except requests.exceptions.RequestException as error:
            print(f"Download failed: {filename} - {error}")


if __name__ == "__main__":
    download_documents()
