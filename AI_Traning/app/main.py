
import json
from pathlib import Path
from app.vectorstore import semantic_search
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.smart_search import search_records
from app.llm import generate_answer

app = FastAPI(
    title="JalSanchay API",
    description="CGWB-based rooftop rainwater harvesting information",
    version="1.1.0"
)

BASE_DIR = Path(__file__).resolve().parent.parent
RECORDS_FILE = BASE_DIR / "data" / "records.json"
QUESTIONS_FILE = BASE_DIR / "data" / "questions.json"
PROMPTS_DIR = BASE_DIR / "prompts"


def load_records():
    try:
        with open(RECORDS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def load_prompt(filename):
    prompt_path = PROMPTS_DIR / filename

    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()


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


@app.post("/chat")
def chat(data: Question):
    question = data.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        records = load_records()
        relevant_records = search_records(records, question)

        # Keep the context small and relevant.
        context = json.dumps(
            relevant_records[:8],
            ensure_ascii=False,
            indent=2
        )

        system_prompt = load_prompt("system.txt")

        # Select a task prompt.
        calculation_words = [
            "calculate", "calculation", "how much",
            "litres", "liters", "capacity", "estimate"
        ]

        if any(word in question.lower() for word in calculation_words):
            task_prompt = load_prompt("calculate_rainwater.txt")
        else:
            task_prompt = load_prompt("answer_question.txt")

        user_prompt = task_prompt.format(
            question=question,
            context=context if relevant_records else "No relevant CGWB records found."
        )

        result = generate_answer(system_prompt, user_prompt)

        return {
            "answer": result["answer"],
            "confidence": result["confidence"],
            "follow_up": result["follow_up"]
        }

    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error))

    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=502, detail=str(error))


@app.get("/search/semantic")
def semantic_search_endpoint(q: str, limit: int = 5):

    if not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    if limit < 1 or limit > 20:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 20"
        )

    try:

        results = semantic_search(q, limit)

        return {
            "query": q,
            "total": len(results),
            "results": results
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

@app.get("/search/semantic")
def semantic_search_endpoint(q: str, limit: int = 5):

    if not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    if limit < 1 or limit > 20:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 20"
        )

    try:
        results = semantic_search(q, limit)

        return {
            "query": q,
            "total": len(results),
            "results": results
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )