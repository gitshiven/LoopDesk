from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from typing import TypedDict
from agent.classifier import classify_ticket
from agent.agents.billing import billing_agent
from agent.agents.technical import technical_agent
from agent.agents.general import general_agent
from agent.confidence import score_confidence, should_escalate

# State definition
class TicketState(TypedDict):
    message: str
    category: str
    response: str
    context_used: str
    confidence: float
    escalated: bool
    escalation_summary: str

# Node functions
def classify_node(state: TicketState) -> TicketState:
    result = classify_ticket(state["message"])
    return {**state, "category": result["category"]}

def billing_node(state: TicketState) -> TicketState:
    result = billing_agent(state["message"])
    return {**state, "response": result["response"], "context_used": result["context_used"]}

def technical_node(state: TicketState) -> TicketState:
    result = technical_agent(state["message"])
    return {**state, "response": result["response"], "context_used": result["context_used"]}

def general_node(state: TicketState) -> TicketState:
    result = general_agent(state["message"])
    return {**state, "response": result["response"], "context_used": result["context_used"]}

def confidence_node(state: TicketState) -> TicketState:
    score = score_confidence(state["message"], state["response"], state["context_used"])
    escalated = should_escalate(score)

    escalation_summary = ""
    if escalated:
        escalation_summary = (
            f"ESCALATION REQUIRED\n"
            f"Category: {state['category']}\n"
            f"Confidence: {score}\n"
            f"Message: {state['message']}\n"
            f"Agent attempted: {state['response']}\n"
            f"Please review and respond manually."
        )

    return {**state, "confidence": score, "escalated": escalated, "escalation_summary": escalation_summary}

# Routing functions
def route_by_category(state: TicketState) -> str:
    return state["category"]

def route_by_confidence(state: TicketState) -> str:
    return "escalate" if state["escalated"] else "resolve"

# Build graph
def build_graph():
    graph = StateGraph(TicketState)

    # Add nodes
    graph.add_node("classify", classify_node)
    graph.add_node("billing", billing_node)
    graph.add_node("technical", technical_node)
    graph.add_node("general", general_node)
    graph.add_node("confidence", confidence_node)

    # Entry point
    graph.set_entry_point("classify")

    # Classify → route to specialist
    graph.add_conditional_edges("classify", route_by_category, {
        "billing": "billing",
        "technical": "technical",
        "general": "general"
    })

    # Specialists → confidence check
    graph.add_edge("billing", "confidence")
    graph.add_edge("technical", "confidence")
    graph.add_edge("general", "confidence")

    # Confidence → resolve or escalate
    graph.add_conditional_edges("confidence", route_by_confidence, {
        "resolve": END,
        "escalate": END
    })

    return graph.compile()

# Run a ticket through the graph
def run_ticket(message: str) -> TicketState:
    graph = build_graph()
    result = graph.invoke({"message": message})
    return result