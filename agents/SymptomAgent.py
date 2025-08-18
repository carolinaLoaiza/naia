import json
from app.GroqChat import GroqChat
from datetime import datetime
import streamlit as st
import re

from app.MedicalRecordManager import MedicalRecordManager
from app.SymptomManager import SymptomManager

def handle_symptom_query(state):
    """
    Handles a user's symptom query, evaluating severity and returning recommendations.

    Args:
        state (dict): Contains user input under the key 'input'.

    Returns:
        dict: Contains the evaluated output message and the username.
    """
    # import local to avoid circular dependency
    from agents.NaiaAgent import NaiaAgent  
    user_input = state["input"]
    username = st.session_state["username"]
    try:
        # Load medical history
        medical_record_manager = MedicalRecordManager(username)
        medical_data = medical_record_manager.record
        # Prepare patient data for symptom evaluation
        patient_data = {
            "surgery": medical_record_manager.get_surgery_info().get("surgery"),
            "medications": medical_record_manager.get_medications(),
            "pre_existing_conditions": medical_record_manager.get_pre_existing_conditions(),
        }
        # Naia instance and pass its function as callback
        naia_agent = NaiaAgent(medical_data)
        agent = SymptomAgent(patient_data, notify_fn=naia_agent.handle_symptom_notification)
        # Evaluate the symptom and generate recommendations
        severity, reco_text = agent.process_symptom(user_input, duration_days=1)
        output = f"🔎 The symptom was evaluated as: **{severity}**."
        if reco_text:
            output += f"\n\n🩺:\n{reco_text}"
        return {"output": output, "username": username}

    except FileNotFoundError:
        return {
            "output": "No medical history found for this user.",
            "username": username,
        }
    
    
class SymptomAgent:
    """
    Agent responsible for analyzing symptoms, classifying severity, 
    and notifying external systems if needed.

    Attributes:
        patient_record (dict): Patient's medical info (surgery, medications, conditions).
        symptom_history (list): Local cache of previous symptoms.
        notify_fn (callable): Optional callback function for notifications.
        username (str): Current user.
        symptom_manager (SymptomManager): Handles storage of symptom entries.
    """
    def __init__(self, patient_record, notify_fn=None):
        """
        Initializes the SymptomAgent with patient data and optional callback.

        Args:
            patient_record (dict): Medical info about the patient.
            notify_fn (callable, optional): Function to notify external agent.
        """
        self.patient_record = patient_record
        self.symptom_history = []
        self.notify_fn = notify_fn
        self.username = st.session_state["username"]
        self.symptom_manager = SymptomManager(self.username)

    def classify_severity_llm(self, symptom: str, duration_days: int) -> str:
        """
        Classifies symptom severity using a language model (GroqChat).

        Args:
            symptom (str): Symptom description.
            duration_days (int): Duration of symptom in days.

        Returns:
            str: Severity level (e.g., Mild, Moderate, Severe).
        """
        groq = GroqChat()
        severity = groq.classify_severity(symptom, self.patient_record, duration_days)
        return severity

    def extract_symptoms(self, text: str) -> list[str]:
        """
        Extracts symptoms mentioned in free-text input.

        Args:
            text (str): User's symptom description.

        Returns:
            list[str]: List of detected symptom strings.
        """
        groq = GroqChat()
        data = groq.extract_symptoms(text)
        if data and "detected_symptoms" in data:
            return data["detected_symptoms"]
        return []

    def process_symptom(self, text: str, duration_days: int = None):
        """
        Processes a symptom input, classifies severity, and records it.

        Args:
            text (str): Symptom description text.
            duration_days (int, optional): Duration of the symptom. Defaults to None.

        Returns:
            tuple: (severity (str), recommendation_text (str))
        """
        groq = GroqChat()
        data = groq.extract_symptoms(text)
        print("Extracted data:", data)
        # Determine symptoms
        symptoms = data.get("detected_symptoms") if data else []
        if not symptoms:
            symptoms = [text]  # fallback: todo como un síntoma

        # Determine duration for each symptom       
        for symptom in data.get("symptoms", []):
            name = symptom.get("name")
            if not name:
                continue
            if symptom.get("duration_days") is None:
                duration_days = groq.extract_duration_from_text(text, name)
                print(f"Duration for '{name}': {duration_days} days")
                if duration_days is None or duration_days <= 0:
                    duration_days = 1
                symptom["duration_days"] = duration_days
        # Classify overall severity    
        severity = self.classify_severity_llm(text, duration_days)

        # Save symptom entry
        now = datetime.now().isoformat()
        entry = {
            "timestamp": now,
            "symptoms": data.get("symptoms", []),
            "overall_severity": severity,
            "input_text": text,
        }
        self.symptom_manager.add_entry(entry)
        # Urgent case handling
        is_urgent = str(severity).lower() == "severe"
        if is_urgent:
            urgent_msg = (
                "🚨 **Potentially urgent symptoms detected.**\n"
                "Please call emergency services or go to the hospital immediately.\n"
                "If you are already in the hospital, inform the medical staff about these symptoms."                
            )            
            return severity, urgent_msg
        # Optional notification callback
        recommendation_text = ""
        if self.notify_fn:
            recommendation_text = self.notify_fn(text, severity) or ""
        return severity, recommendation_text   
    
    def get_symptom_duration(self, symptom: str) -> int:
        """
        Returns the duration in days since the last report of the given symptom.

        Args:
            symptom (str): Name of the symptom.

        Returns:
            int: Duration in days (defaults to 1 if not found).
        """
        for entry in self.symptom_history:
            if entry["symptom"].lower() == symptom.lower():
                timestamp = datetime.fromisoformat(entry["timestamp"])
                return (datetime.now() - timestamp).days + 1
        return 1
    
