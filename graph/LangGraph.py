from langgraph.graph import StateGraph
from agents.NaiaAgent import classify_intent

from agents.ReminderAgent import handle_reminder_query
from agents.ChatAgent import handle_chat
from agents.SymptomAgent import handle_symptom_query
from agents.MedicalRecordAgent import handle_medical_record_query
from agents.HealthRecommendationAgent import handle_recommendation_query
from typing import TypedDict
from agents.AgentState import AgentState
    
# the node acts as a router: should be declared before the nodes it routes to
def router_node(state: AgentState) -> AgentState:
    # Just pass the state so that LangGraph can use classify_intent to decide which node to go to
    return state

def build_graph():
    builder = StateGraph(AgentState)

    # Node that checks for pending medication reminders
    builder.add_node("check_reminder", check_reminder_node)

    # Add the router node
    builder.add_node("router", router_node)

    # Agent nodes
    builder.add_node("symptom_agent", handle_symptom_query)
    builder.add_node("recommendation_agent", handle_recommendation_query)
    builder.add_node("medical_record_agent", handle_medical_record_query)
    builder.add_node("reminder_agent", handle_reminder_query)
    builder.add_node("chat_agent", handle_chat)

    # The conditional decision comes from the router
    #builder.add_conditional_edges("router", classify_intent)

    # Connections
    builder.add_edge("check_reminder", "router")  # check_reminder runs first
    # Define entry and exit points
    builder.add_conditional_edges("router", classify_intent)    
    #builder.set_entry_point("router")
    builder.set_entry_point("check_reminder")

    builder.set_finish_point("symptom_agent")
    builder.set_finish_point("medical_record_agent")
    builder.set_finish_point("recommendation_agent")
    builder.set_finish_point("reminder_agent")
    builder.set_finish_point("chat_agent")

    return builder.compile()

def check_reminder_node(state: AgentState) -> AgentState:
    from agents.ReminderAgent import load_tracker, check_pending_medications  # importa aquí si no está disponible arriba
    username = state.get("username")
    tracker = load_tracker(username)
    upcoming = check_pending_medications(tracker)
    reminder_msg = ""
    if upcoming:
        reminder_msg = "💊 **Reminder**:\n" + "\n".join(upcoming) + "\n\n"

    state["reminder"] = reminder_msg
    return state