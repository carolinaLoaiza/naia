from app.GroqChat import GroqChat

router = GroqChat()

def classify_intent(state: dict) -> str:
    user_input = state["input"]

    prompt = f"""
    You are a routing assistant for a multi-agent healthcare assistant.

    Given a user's message, decide which agent should handle it:

    - "health_agent": if the user mentions symptoms, pain, discomfort, or medical questions
    - "reminder_agent": if the user wants to set or check reminders, appointments, or medication schedules
    - "chat_agent": if it's a general conversation or question not related to health or reminders

    Examples:
    - "I have pain in my leg" → health_agent  
    - "Can you remind me to take my medicine?" → reminder_agent  
    - "Set a reminder for my next pill at 9 PM" → reminder_agent  
    - "Hi, how are you?" → chat_agent  
    - "What can I do for a headache?" → health_agent  
    - "Is it going to rain today?" → chat_agent  
    - "Remind me about my appointment tomorrow" → reminder_agent  
    - "I feel dizzy and nauseous" → health_agent
    Respond with just one of these: health_agent, reminder_agent, or chat_agent.

    User message: "{user_input}"
    """

    result = router.get_chat_response(prompt)  # or whatever call you use
    print("Routing to:", result)  # <-- esto
    return result.strip().lower()
