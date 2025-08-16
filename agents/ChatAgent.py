import streamlit as st
from agents.AgentState import AgentState

def handle_chat(state: AgentState) -> AgentState:
    reminder = state.get("reminder", "")
    user_input = state.get("input", "")
    username = state.get("username")
    default_response =  (
        "ℹ️ NAIA is here to support your health and recovery after surgery, based on your medical history and current symptoms.\n"
        "This question falls outside the scope of what I can safely help with.\n"
        "If you have any concerns related to your health, recovery, medications, or symptoms, I'm here for you."
    )    
    full_response = f"{reminder}{default_response}"
    return {
        "input": user_input,
        "output": full_response,
        "username": username,
        "reminder": ""
    }