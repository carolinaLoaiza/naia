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

    Given a user's message, decide which agent should handle it:

    - "symptom_agent": if the user is describing symptoms (e.g., "it hurts", "I have a fever", etc.)
    - "medical_record_agent": if the user is asking about allergies, prescriptions, surgeries, or medical history
    - "recommendation_agent": if the user is asking for advice, what to do, next steps, etc.
    - "reminder_agent": if the user wants to create/check reminders for medications or appointments
    - "chat_agent": if the user is being friendly or asking general things (e.g., "how are you?", "what's your name?")

    If MULTIPLE categories apply, PRIORITIZE "symptom_agent" first.
    Respond with just one of these: symptom_agent, medical_record_agent, recommendation_agent, reminder_agent, chat_agent.

    Examples:
    - "I have pain in my leg" → symptom_agent 
    - "Can you remind me to take my medicine?" → reminder_agent  
    - "Set a reminder for my next pill at 9 PM" → reminder_agent  
    - "Hi, how are you?" → chat_agent  
    - "What can I do for a headache?" → recommendation_agent  
    - "Am I allergic to anything?" → medical_record_agent  
    - "Do I have any upcoming surgeries?" → medical_record_agent  
    - "I feel dizzy and nauseous" → symptom_agent  
    - "Is this pain normal after my operation?" → recommendation_agent  
    - "What was my prescription again?" → medical_record_agent  
    - "Should I go to the hospital for chest pain?" → recommendation_agent  

    User message: "{user_input}"
    """

    result = router.get_chat_response(prompt)  # or whatever call you use
    print("Routing to:", result)  # <-- esto
    return result.strip().lower()


#    - "health_agent": if the user mentions symptoms, pain, discomfort, or medical questions
#    - "reminder_agent": if the user wants to set or check reminders, appointments, or medication schedules
#    - "chat_agent": if it's a general conversation or question not related to health or reminders
