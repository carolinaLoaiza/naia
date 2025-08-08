from app.GroqChat import GroqChat
from agents.HealthRecommendationAgent import handle_recommendation_query
from agents.HealthRecommendationAgent import handle_recommendation_query_with_symptoms
import streamlit as st

router = GroqChat()

class NaiaAgent:
    def __init__(self, medical_record: dict):
        self.medical_record = medical_record

    def handle_symptom_notification(self, symptom: str, severity: str):
        print(f"📬 NaiaAgent received the symptom '{symptom}' con severidad '{severity}'")
        state = {
            "input": f"I have the symptom '{symptom}' classified as '{severity}'. What medical recommendations are there?",
            "username": st.session_state.get("username")
        }
        response = handle_recommendation_query_with_symptoms(state)
        #print("💡 Recommendation sent by NaiaAgent:", response.get("output"))
        return response.get("output", "")



def classify_intent(state: dict) -> str:
    user_input = state["input"]

    prompt = f"""
    You are a routing assistant for a multi-agent healthcare assistant.

    Your task is to classify the user's message into one of these agents:
    
    - "symptom_agent": if the user is describing physical symptoms (e.g., "I have pain", "I'm nauseous", "It hurts")
    - "reminder_medication_agent": if the user asks to check, create, confirm, or modify any medication reminders (e.g., "Did I take my ibuprofen?", "Remind me to take my pills")
    - "reminder_recovery_agent": if the user asks to check, create, confirm, or modify any recovery task reminders (e.g., "What stretches do I need to do today?", "When should I apply ice?")
    - "medical_record_agent": if the user is asking about general medical history like allergies, past prescriptions, surgeries, or lab results
    - "recommendation_agent": if the user wants medical advice or next steps (e.g., "what should I do?", "is this normal?", "should I go to the hospital?")
    - "chat_agent": if the user is being friendly or casual (e.g., "how are you?", "what's your name?")

    If MULTIPLE categories seem relevant, follow this priority:
    1. symptom_agent  
    2. reminder_medication_agent
    3. reminder_recovery_agent
    4. medical_record_agent  
    5. recommendation_agent  
    6. chat_agent

    Respond with ONLY one of: symptom_agent, reminder_medication_agent, reminder_recovery_agent, medical_record_agent, recommendation_agent, chat_agent

    Examples:
    - "I have pain in my leg" → symptom_agent
    - "Remind me to take my pills at 8pm" → reminder_medication_agent
    - "Did I take my ibuprofen?" → reminder_medication_agent
    - "What stretches do I need to do today?" → reminder_recovery_agent
    - "When should I apply ice?" → reminder_recovery_agent
    - "What were my last test results?" → medical_record_agent
    - "Do I have any allergies?" → medical_record_agent
    - "Should I go to the ER?" → recommendation_agent
    - "Hey, how are you?" → chat_agent

    User message: "{user_input}"
    """

    result = router.get_chat_response(prompt)  # or whatever call you use
    print("Routing to:", result)  # <-- esto
    return result.strip().lower()

