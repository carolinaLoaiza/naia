# Puedes reemplazar esta función por tu función real de Groq si ya tienes una
def handle_chat(state):
    user_input = state["input"]
    return {"output": f"🗨️ Esta es una respuesta general para: '{user_input}'"}
