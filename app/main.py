
import json
import logging
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI, HTTPException
from langgraph.types import Command
from pydantic import BaseModel

from app.graph import agent_graph
from app.llm import generate_answer
from app.rag import answer_question
from app.response_cache import response_cache
from app.smart_search import search_records
from app.vectorstore import build_index, get_collection, semantic_search

logger = logging.getLogger("jalsanchay.api")
logger.setLevel(logging.INFO)

if not logger.handlers:
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    )
    logger.addHandler(log_handler)

logger.propagate = False
app = FastAPI(
    title="JalSanchay API",
    description="CGWB-based rooftop rainwater harvesting information",
    version="1.2.0"
)
@app.on_event("startup")
def initialize_vector_database():
    collection = get_collection()

    if collection.count() == 0:
        print("Chroma database is empty. Building index...")
        build_index()
    else:
        print(f"Chroma database already contains {collection.count()} chunks.")



BASE_DIR = Path(__file__).resolve().parent.parent
RECORDS_FILE = BASE_DIR / "data" / "records.json"
QUESTIONS_FILE = BASE_DIR / "data" / "questions.json"
PROMPTS_DIR = BASE_DIR / "prompts"



class Question(BaseModel):
    question: str


class AgentRequest(BaseModel):
    question: str = ""
    calculator_inputs: dict | None = None
    top_k: int = 5
    thread_id: str
    approved: bool | None = None




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




@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "JalSanchay"
    }




@app.get("/records")
def get_records(limit: int = 100):
    records = load_records()
    return records[:max(0, limit)]


@app.get("/records/{record_id}")
def get_record(record_id: int):
    records = load_records()

    if record_id < 1 or record_id > len(records):
        raise HTTPException(
            status_code=404,
            detail="Record not found"
        )

    return records[record_id - 1]




@app.get("/search")
def search(q: str):
    records = load_records()

    if not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    results = search_records(records, q)

    return {
        "query": q,
        "total": len(results),
        "results": results
    }



@app.post("/questions")
def submit_question(data: Question):
    question = data.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        if QUESTIONS_FILE.exists():
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
                questions = json.load(file)
        else:
            questions = []

        questions.append({"question": question})

        with open(QUESTIONS_FILE, "w", encoding="utf-8") as file:
            json.dump(
                questions,
                file,
                indent=4,
                ensure_ascii=False
            )

        return {
            "message": "Question submitted successfully",
            "question": question
        }

    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )




@app.post("/chat")
def chat(data: Question):
    question = data.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        records = load_records()
        relevant_records = search_records(records, question)

        context = json.dumps(
            relevant_records[:8],
            ensure_ascii=False,
            indent=2
        )

        system_prompt = load_prompt("system.txt")

        calculation_words = [
            "calculate",
            "calculation",
            "how much",
            "litres",
            "liters",
            "capacity",
            "estimate"
        ]

        if any(word in question.lower() for word in calculation_words):
            task_prompt = load_prompt("calculate_rainwater.txt")
        else:
            task_prompt = load_prompt("answer_question.txt")

        user_prompt = task_prompt.format(
            question=question,
            context=(
                context
                if relevant_records
                else "No relevant CGWB records found."
            )
        )

        result = generate_answer(system_prompt, user_prompt)

        return {
            "answer": result["answer"],
            "confidence": result["confidence"],
            "follow_up": result["follow_up"]
        }

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    except (ValueError, RuntimeError) as error:
        raise HTTPException(
            status_code=502,
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





@app.post("/ask")
def ask_question_endpoint(q: str, top_k: int = 5):
    start_time = perf_counter()
    cache_hit = False
    usage = {}

    try:
        if not q.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )

        if len(q) > 2000:
            raise HTTPException(
                status_code=413,
                detail="Question cannot exceed 2000 characters"
            )

        if top_k < 1 or top_k > 20:
            raise HTTPException(
                status_code=400,
                detail="top_k must be between 1 and 20"
            )

        cache_key = (q.strip().lower(), top_k)
        cached_result = response_cache.get(cache_key)

        if cached_result is not None:
            cache_hit = True
            return cached_result

        result = answer_question(q, top_k)

        usage = result.pop("_usage", {}) or {}
        response_cache.set(cache_key, result)

        return result

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

    finally:
        latency_ms = round(
            (perf_counter() - start_time) * 1000,
            2
        )

        logger.info(
            "ask_request latency_ms=%s cache_hit=%s "
            "prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            latency_ms,
            cache_hit,
            usage.get("prompt_tokens", 0) if not cache_hit else 0,
            usage.get("completion_tokens", 0) if not cache_hit else 0,
            usage.get("total_tokens", 0) if not cache_hit else 0
        )






@app.post("/agent")
def agent_endpoint(data: AgentRequest):

    thread_id = data.thread_id.strip()

    if not thread_id:
        raise HTTPException(
            status_code=400,
            detail="thread_id cannot be empty"
        )

    if data.top_k < 1 or data.top_k > 20:
        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 20"
        )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:

       
        if data.approved is not None:

            snapshot = agent_graph.get_state(config)

            if not snapshot.next:
                raise HTTPException(
                    status_code=400,
                    detail="No pending approval for this thread."
                )

            result = agent_graph.invoke(
                Command(
                    resume={"approved": data.approved}
                ),
                config=config
            )

        else:

            question = data.question.strip()

            if not question:
                raise HTTPException(
                    status_code=400,
                    detail="Question cannot be empty"
                )

            result = agent_graph.invoke(
                {
                    "question": question,
                    "calculator_inputs": data.calculator_inputs,
                    "top_k": data.top_k
                },
                config=config
            )

        snapshot = agent_graph.get_state(config)

     
        if snapshot.next:

            return {
                "status": "approval_required",
                "thread_id": thread_id,
                "approval_request": (
                    snapshot.tasks[0].interrupts[0].value
                )
            }

        return {
            "status": "completed",
            "thread_id": thread_id,
            "result": result.get("result")
        }

    except HTTPException:
        raise

    except (ValueError, RuntimeError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
