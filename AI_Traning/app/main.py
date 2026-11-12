
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.smart_search import search_records

app = FastAPI(
    title="JalSanchay API",
    description="CGWB-based rooftop rainwater harvesting information",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent.parent
RECORDS_FILE = BASE_DIR / "data" / "records.json"
QUESTIONS_FILE = BASE_DIR / "data" / "questions.json"


def load_records():
    try:
        with open(RECORDS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


class Question(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "healthy", "service": "JalSanchay"}


@app.get("/records")
def get_records(limit: int = 100):
    records = load_records()
    return records[:max(0, limit)]


@app.get("/records/{record_id}")
def get_record(record_id: int):
    records = load_records()

    if record_id < 1 or record_id > len(records):
        raise HTTPException(status_code=404, detail="Record not found")

    return records[record_id - 1]


@app.get("/search")
def search(q: str):
    records = load_records()

    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    results = search_records(records, q)
    return {"query": q, "total": len(results), "results": results}


@app.post("/questions")
def submit_question(data: Question):
    question = data.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        if QUESTIONS_FILE.exists():
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
                questions = json.load(file)
        else:
            questions = []

        questions.append({"question": question})

        with open(QUESTIONS_FILE, "w", encoding="utf-8") as file:
            json.dump(questions, file, indent=4, ensure_ascii=False)

        return {
            "message": "Question submitted successfully",
            "question": question
        }

    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=500, detail=str(error))
