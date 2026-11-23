
import json
import os
from pathlib import Path

import httpx
from dotenv import dotenv_values, load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


def extract_json(text):
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("LLM did not return valid JSON")

        data = json.loads(text[start:end + 1])

    answer = str(data.get("answer", "")).strip()
    follow_up = str(data.get("follow_up", "")).strip()

    try:
        confidence = float(data.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0.0

    confidence = max(0.0, min(1.0, confidence))

    if not answer:
        raise ValueError("LLM returned an empty answer")

    return {
        "answer": answer,
        "confidence": confidence,
        "follow_up": follow_up
    }


def generate_answer(system_prompt, user_prompt):

    # Reload the project's .env whenever a request is made.
    load_dotenv(ENV_FILE, override=True)

    # Read directly from .env as a fallback.
    env_values = dotenv_values(ENV_FILE)

    provider = (
        os.getenv("LLM_PROVIDER")
        or env_values.get("LLM_PROVIDER")
        or "gemini"
    ).lower().strip()

    if provider == "gemini":

        api_key = (
            os.getenv("GEMINI_API_KEY")
            or env_values.get("GEMINI_API_KEY")
        )

        model = (
            os.getenv("GEMINI_MODEL")
            or env_values.get("GEMINI_MODEL")
            or "gemini-3.8-flash"
        )

        if not api_key or not api_key.strip():
            raise ValueError(
                f"Gemini API key not found. "
                f"Checked file: {ENV_FILE}. "
                f"File exists: {ENV_FILE.exists()}"
            )

        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/{model}:generateContent"
        )

        headers = {
            "x-goog-api-key": api_key.strip(),
            "Content-Type": "application/json"
        }

        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

    elif provider == "groq":

        api_key = (
            os.getenv("GROQ_API_KEY")
            or env_values.get("GROQ_API_KEY")
        )

        model = (
            os.getenv("GROQ_MODEL")
            or env_values.get("GROQ_MODEL")
            or "llama-3.3-70b-versatile"
        )

        if not api_key or not api_key.strip():
            raise ValueError("GROQ_API_KEY is missing in .env")

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt + "\nReturn your response in valid JSON format."
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

    else:
        raise ValueError("LLM_PROVIDER must be gemini or groq")

    try:
        response = httpx.post(
            url,
            headers=headers,
            json=payload,
            timeout=60.0
        )

        response.raise_for_status()
        result = response.json()

        if provider == "gemini":
            response_text = (
            result["candidates"][0]["content"]["parts"][0]["text"]
            )

            usage_data = result.get("usageMetadata", {})

            usage = {
                "prompt_tokens": usage_data.get("promptTokenCount"),
                "completion_tokens": usage_data.get("candidatesTokenCount"),
                "total_tokens": usage_data.get("totalTokenCount")
            }

        else:
            response_text = result["choices"][0]["message"]["content"]

            usage_data = result.get("usage", {})

            usage = {
                "prompt_tokens": usage_data.get("prompt_tokens"),
                "completion_tokens": usage_data.get("completion_tokens"),
                "total_tokens": usage_data.get("total_tokens")
            }

        answer_data = extract_json(response_text)
        answer_data["_usage"] = usage

        return answer_data

    except httpx.HTTPStatusError as error:
        raise RuntimeError(
            f"{provider} API error: "
            f"{error.response.status_code} - "
            f"{error.response.text[:500]}"
        ) from error

    except (httpx.RequestError, KeyError, IndexError) as error:
        raise RuntimeError(
            f"Could not get response from {provider}: {error}"
        ) from error
