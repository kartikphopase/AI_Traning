
from typing import Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from app.rag import answer_question
from app.tools import rooftop_rainwater_calculator


class AgentState(TypedDict, total=False):
    question: str
    calculator_inputs: dict[str, Any]
    top_k: int
    action: str
    approval: dict
    result: dict


def decide_action(state: AgentState):
    question = state["question"].lower()

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

    if any(word in question for word in calculation_keywords):
        return {"action": "calculator"}

    return {"action": "rag"}


def route_action(state: AgentState):
    if state["action"] == "calculator":
        if not state.get("calculator_inputs"):
            return "needs_input"
        return "approval"

    return "rag"


def needs_input(state: AgentState):
    return {
        "result": {
            "agent_action": "rooftop_rainwater_calculator",
            "status": "needs_input",
            "message": "Please provide all six calculator inputs.",
            "required_inputs": [
                "rainfall_mm",
                "roof_area_sqm",
                "roof_type",
                "persons",
                "litres_per_person_per_day",
                "dry_days"
            ]
        }
    }


def request_approval(state: AgentState):
    approval = interrupt({
        "message": "Approval required before calculating rainwater collection.",
        "calculator_inputs": state["calculator_inputs"]
    })

    return {"approval": approval}


def route_approval(state: AgentState):
    if state.get("approval", {}).get("approved") is True:
        return "calculator"

    return "rejected"


def run_calculator(state: AgentState):
    result = rooftop_rainwater_calculator(
        **state["calculator_inputs"]
    )

    return {
        "result": {
            "agent_action": "rooftop_rainwater_calculator",
            "status": "success",
            "result": result
        }
    }


def run_rag(state: AgentState):
    result = answer_question(
        state["question"],
        top_k=state.get("top_k", 5)
    )

    return {
        "result": {
            "agent_action": "rag_search",
            "status": "success",
            "result": result
        }
    }


def reject_calculation(state: AgentState):
    return {
        "result": {
            "agent_action": "rooftop_rainwater_calculator",
            "status": "rejected",
            "message": "Calculator execution was not approved."
        }
    }


# Build the LangGraph workflow
builder = StateGraph(AgentState)

builder.add_node("decide", decide_action)
builder.add_node("needs_input", needs_input)
builder.add_node("approval", request_approval)
builder.add_node("calculator", run_calculator)
builder.add_node("rag", run_rag)
builder.add_node("rejected", reject_calculation)

builder.add_edge(START, "decide")

builder.add_conditional_edges(
    "decide",
    route_action,
    {
        "needs_input": "needs_input",
        "approval": "approval",
        "rag": "rag"
    }
)

builder.add_conditional_edges(
    "approval",
    route_approval,
    {
        "calculator": "calculator",
        "rejected": "rejected"
    }
)

builder.add_edge("needs_input", END)
builder.add_edge("calculator", END)
builder.add_edge("rag", END)
builder.add_edge("rejected", END)

# Memory/checkpoint storage
memory = InMemorySaver()

agent_graph = builder.compile(checkpointer=memory)
