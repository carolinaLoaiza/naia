from app.GroqChat import GroqChat
from typing import Dict, List, Optional



def handle_medical_record_query(state):
    user_input = state["input"]
    return {"output": f"🗨️ This is a handle_medical_record_query: '{user_input}'"}


class MedicalRecordAgent:
    def __init__(self, medical_history: Dict, symptoms_history: List[Dict], chat_history: List[Dict]):
        self.medical_history = medical_history
        self.symptoms_history = symptoms_history
        self.chat_history = chat_history
        self.groq = GroqChat()

    def build_prompt(self, user_question: str) -> str:
        # Convierte la info en texto para el prompt
        medical_history_text = f"Medical History:\n{self._dict_to_text(self.medical_history)}"
        symptoms_text = "Symptoms History:\n" + "\n".join(
            [f"- {s['symptom']} (severity: {s.get('severity', 'unknown')})" for s in self.symptoms_history]
        )
        chat_text = "Chat History:\n" + "\n".join(
            [f"User: {msg.get('user', '')}\nAgent: {msg.get('agent', '')}" for msg in self.chat_history]
        )

        prompt = f"""
        You are a knowledgeable medical assistant. Use only the patient information provided below to answer the question.
        Do NOT guess or provide information not present in the data.

        {medical_history_text}

        {symptoms_text}

        {chat_text}

        Question: {user_question}

        Please provide a clear, concise, and factual answer based only on the data above.
        """
        return prompt

    def _dict_to_text(self, d: Dict) -> str:
        # Función simple para convertir diccionario en texto legible
        lines = []
        for k, v in d.items():
            if isinstance(v, list):
                lines.append(f"{k}: {', '.join(map(str, v))}")
            else:
                lines.append(f"{k}: {v}")
        return "\n".join(lines)

    def answer_question(self, user_question: str) -> str:
        prompt = self.build_prompt(user_question)
        response = self.groq.get_chat_response(prompt)
        return response.strip()
