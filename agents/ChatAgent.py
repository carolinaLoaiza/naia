import streamlit as st
from agents.AgentState import AgentState

def handle_chat(state: AgentState) -> AgentState:
    """
    Generates a response for user input and updates the agent state.

    Args:
        state (AgentState): Current agent state containing input, output,
                            username, and reminder.

    Returns:
        AgentState: Updated state with the generated response.
    """
    reminder = state.get("reminder", "")
    user_input = state.get("input", "")
    username = state.get("username")

     # Default response shown when the input falls outside supported topics
    default_response =  (
        "ℹ️ NAIA is here to support your health and recovery after surgery, based on your medical history and current symptoms.\n"
        "This question falls outside the scope of what I can safely help with.\n"
        "If you have any concerns related to your health, recovery, medications, or symptoms, I'm here for you."
    )   
     
    # Combine reminder (if any) with the default response
    full_response = f"{reminder}{default_response}"
    # Return the updated agent state
    return {
        "input": user_input,
        "output": full_response,
        "username": username,
        "reminder": ""
    }