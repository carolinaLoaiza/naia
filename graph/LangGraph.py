from langgraph.graph import StateGraph
from agents.NaiaAgent import classify_intent
from agents.HealthAgent import handle_health_query
from agents.ReminderAgent import handle_reminder_query
from agents.ChatAgent import handle_chat
from typing import TypedDict


class AgentState(TypedDict):
    input: str
    output: str

# El nodo que actúa como router: debe ser declarado
def router_node(state: AgentState) -> AgentState:
    # Sólo pasa el estado para que luego LangGraph use classify_intent para decidir a qué nodo ir
    return state

def build_graph():
    builder = StateGraph(AgentState)

    # Añadir el nodo router
    builder.add_node("router", router_node)

    # Nodos agentes
    builder.add_node("health_agent", handle_health_query)
    builder.add_node("reminder_agent", handle_reminder_query)
    builder.add_node("chat_agent", handle_chat)

    # La decisión condicional sale desde router
    builder.add_conditional_edges("router", classify_intent)

    # Definimos nodo inicial y final
    builder.set_entry_point("router")
    
    builder.set_finish_point("health_agent")
    builder.set_finish_point("reminder_agent")
    builder.set_finish_point("chat_agent")

    return builder.compile()