from agents.AgentState import AgentState
from app.GroqChat import GroqChat
from typing import Dict, List, Optional

from app.MedicalRecordManager import MedicalRecordManager
from app.SymptomManager import SymptomManager

agent_instance = None  # cache global


def handle_medical_record_query(state: AgentState) -> AgentState:
    global agent_instance
    username = state["username"]
    user_input = state["input"]
    reminder = state.get("reminder", "")
    record_manager = MedicalRecordManager(username)
    medical_history = record_manager.record  # todo el JSON como dict
    if not medical_history:
        response = "⚠️ No medical record found for this user."
    else:
        symptom_manager = SymptomManager(username)
        symptoms = symptom_manager.get_all()
        agent = MedicalRecordAgent(
            medical_history=medical_history,
            symptoms_history=symptoms
        )
        response = agent.answer_question(user_input)

    full_response = f"{reminder}{response}"
    return {
        "input": user_input,
        "output": full_response,
        "username": username,
        "reminder": state.get("reminder", "")
    }


class MedicalRecordAgent:
    def __init__(self, medical_history: Dict, symptoms_history: List[Dict]):
        self.medical_history = medical_history
        self.symptoms_history = symptoms_history
        self.groq = GroqChat()

    def build_prompt(self, user_question: str) -> str:
        # Convierte la info en texto para el prompt
        medical_history_text = f"Medical History:\n{self._dict_to_text(self.medical_history)}"
        symptoms_list = []
        for entry in self.symptoms_history:
            for symptom in entry.get("symptoms", []):
                name = symptom.get("name", "unknown symptom")
                severity = symptom.get("severity") or entry.get("overall_severity", "unknown")
                symptoms_list.append(f"- {name} (severity: {severity})")

        symptoms_text = "Symptoms History:\n" + "\n".join(symptoms_list)

        patient_name = self.medical_history.get("name", "Patient")

        prompt = f"""
        You are a knowledgeable medical assistant. Use only the patient information provided below to answer the question.
        Do NOT guess or provide information not present in the data.

        {medical_history_text}
        {symptoms_text}
        Question: {user_question}

        Please provide a clear, concise, and factual answer based only on the data above.
        Start your answer like this:
            "According to your medical records, {patient_name}:"
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
