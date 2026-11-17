
from app.rag import answer_question
from app.tools import rooftop_rainwater_calculator


def run_agent(question: str, calculator_inputs: dict = None, top_k: int = 5):
    """
    Hand-written JalSanchay agent.
    Chooses between the rainwater calculator and RAG search.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    question_lower = question.lower()

    calculation_keywords = [
        "calculate",
        "calculation",
        "how much water",
        "water collection",
        "rainwater collection",
        "water demand",
        "rainwater potential",
        "rooftop potential"
    ]

    # Agent decides which tool to call
    use_calculator = (
        calculator_inputs is not None
        or any(keyword in question_lower for keyword in calculation_keywords)
    )

    if use_calculator:

        # Check whether calculator inputs are provided
        if calculator_inputs is None:
            return {
                "agent_action": "rooftop_rainwater_calculator",
                "status": "needs_input",
                "message": (
                    "Please provide rainfall, roof area, roof type, "
                    "number of persons, daily water requirement, "
                    "and dry days."
                ),
                "required_inputs": [
                    "rainfall_mm",
                    "roof_area_sqm",
                    "roof_type",
                    "persons",
                    "litres_per_person_per_day",
                    "dry_days"
                ]
            }

        # Call calculator tool
        result = rooftop_rainwater_calculator(**calculator_inputs)

        return {
            "agent_action": "rooftop_rainwater_calculator",
            "status": "success",
            "result": result
        }

    # Otherwise, use RAG search
    rag_result = answer_question(question, top_k=top_k)

    return {
        "agent_action": "rag_search",
        "status": "success",
        "result": rag_result
    }
