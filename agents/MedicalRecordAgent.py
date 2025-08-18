from agents.AgentState import AgentState
from app.GroqChat import GroqChat
from typing import Dict, List, Optional

from app.MedicalRecordManager import MedicalRecordManager
from app.SymptomManager import SymptomManager

agent_instance = None  # cache global


def handle_medical_record_query(state: AgentState) -> AgentState:
    """
    Handles a query related to the patient's medical record.

    Args:
        state (AgentState): Current state containing user input, username, and reminder.

    Returns:
        AgentState: Updated state with the agent's response.
    """
    global agent_instance
    username = state["username"]
    user_input = state["input"]
    reminder = state.get("reminder", "")
    # Load patient medical record
    record_manager = MedicalRecordManager(username)
    medical_history = record_manager.record  # todo el JSON como dict
    if not medical_history:
        response = "⚠️ No medical record found for this user."
    else:
        # Load patient symptoms and build an agent
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
    """
    Agent for answering questions based on a patient's medical record
    and symptom history.
    """
    def __init__(self, medical_history: Dict, symptoms_history: List[Dict]):
        self.medical_history = medical_history
        self.symptoms_history = symptoms_history
        self.groq = GroqChat()

    def build_prompt(self, user_question: str) -> str:
        """
        Builds a prompt for the language model using the medical history
        and symptom history.
        """
        medical_history_text = f"Medical History:\n{self._dict_to_text(self.medical_history)}"
        # Format symptoms into readable text
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
        """Converts a dictionary into readable text format."""
        lines = []
        for k, v in d.items():
            if isinstance(v, list):
                lines.append(f"{k}: {', '.join(map(str, v))}")
            else:
                lines.append(f"{k}: {v}")
        return "\n".join(lines)

    def answer_question(self, user_question: str) -> str:
        """Generates an answer to the user’s question using the language model."""
        prompt = self.build_prompt(user_question)
        response = self.groq.get_chat_response(prompt)
        return response.strip()
