import pytest
from fastapi.testclient import TestClient

from app.graph import run_calculator
from app.main import app
from app.tools import rooftop_rainwater_calculator

client = TestClient(app)


@pytest.fixture
def sample_records():
    return [
        {
            "topic": "Roof runoff coefficient",
            "document": "CGWB Manual",
            "section": "7.2.7",
            "rule_or_value": "GI Sheet: 0.9",
            "unit": "coefficient",
            "source_url": "https://example.com/manual.pdf",
        },
        {
            "topic": "Storage tank capacity",
            "document": "CGWB Manual",
            "section": "7.3",
            "rule_or_value": "Tank storage guidance",
            "unit": "litres",
            "source_url": "https://example.com/manual.pdf",
        },
    ]


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_records(monkeypatch, sample_records):
    monkeypatch.setattr("app.main.load_records", lambda: sample_records)
    response = client.get("/records")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_records_with_limit(monkeypatch, sample_records):
    monkeypatch.setattr("app.main.load_records", lambda: sample_records)
    response = client.get("/records?limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_record_by_id(monkeypatch, sample_records):
    monkeypatch.setattr("app.main.load_records", lambda: sample_records)
    response = client.get("/records/1")
    assert response.status_code == 200
    assert response.json()["topic"] == "Roof runoff coefficient"


def test_get_record_not_found(monkeypatch, sample_records):
    monkeypatch.setattr("app.main.load_records", lambda: sample_records)
    response = client.get("/records/99")
    assert response.status_code == 404


def test_search_endpoint(monkeypatch, sample_records):
    monkeypatch.setattr("app.main.load_records", lambda: sample_records)
    monkeypatch.setattr(
        "app.main.search_records",
        lambda records, query: [records[0]],
    )
    response = client.get("/search?q=roof")
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_search_rejects_empty_query():
    response = client.get("/search?q=%20%20")
    assert response.status_code == 400


def test_ask_endpoint_uses_fake_answer(monkeypatch):
    fake_answer = {
        "answer": "Test answer",
        "confidence": 0.9,
        "follow_up": "Test follow-up",
    }
    monkeypatch.setattr(
        "app.main.answer_question",
        lambda question, top_k: fake_answer,
    )
    response = client.post("/ask?q=Test%20question")
    assert response.status_code == 200
    assert response.json() == fake_answer


def test_ask_rejects_invalid_top_k():
    response = client.post("/ask?q=Test%20question&top_k=0")
    assert response.status_code == 400


def test_rainwater_calculator():
    result = rooftop_rainwater_calculator(
        800, 100, "tiled roof", 5, 135, 60
    )
    assert result["annual_rainwater_collection_litres"] == 60000
    assert result["household_demand_litres"] == 40500
    assert result["surplus_or_deficit_litres"] == 19500
    assert result["demand_covered"] is True


def test_calculator_rejects_unsupported_roof():
    with pytest.raises(ValueError):
        rooftop_rainwater_calculator(
            800, 100, "plastic roof", 5, 135, 60
        )


def test_agent_calculator_node():
    state = {
        "calculator_inputs": {
            "rainfall_mm": 800,
            "roof_area_sqm": 100,
            "roof_type": "tiled roof",
            "persons": 5,
            "litres_per_person_per_day": 135,
            "dry_days": 60,
        }
    }
    result = run_calculator(state)
    assert result["result"]["status"] == "success"
    assert (
        result["result"]["result"]["annual_rainwater_collection_litres"]
        == 60000
    )
