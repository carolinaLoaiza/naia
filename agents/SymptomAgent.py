import json
from app.GroqChat import GroqChat
from datetime import datetime
import streamlit as st
import re

from app.MedicalRecordManager import MedicalRecordManager
from app.SymptomManager import SymptomManager

def handle_symptom_query(state):
    from agents.NaiaAgent import NaiaAgent  # import local to avoid circular dependency
    user_input = state["input"]
    username = st.session_state["username"]
    try:
        # Load medical history
        medical_record_manager = MedicalRecordManager(username)
        medical_data = medical_record_manager.record

        patient_data = {
            "surgery": medical_record_manager.get_surgery_info().get("surgery"),
            "medications": medical_record_manager.get_medications(),
            "pre_existing_conditions": medical_record_manager.get_pre_existing_conditions(),
        }
        # Naia instance and pass its function as callback
        naia_agent = NaiaAgent(medical_data)
        agent = SymptomAgent(patient_data, notify_fn=naia_agent.handle_symptom_notification)
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
    def __init__(self, patient_record, notify_fn=None):
        """
        patient_record: dict with relevant data (surgery, medications, conditions, previous symptoms)
        """
        self.patient_record = patient_record
        self.symptom_history = []
        self.notify_fn = notify_fn  # function to invoke from NaiaAgent

        self.username = st.session_state["username"]
        self.symptom_manager = SymptomManager(self.username)

    def classify_severity_llm(self, symptom: str, duration_days: int) -> str:
        groq = GroqChat()
        severity = groq.classify_severity(symptom, self.patient_record, duration_days)
        return severity

    def extract_symptoms(self, text: str) -> list[str]:
        groq = GroqChat()
        data = groq.extract_symptoms(text)
        if data and "detected_symptoms" in data:
            return data["detected_symptoms"]
        return []

    def process_symptom(self, text: str, duration_days: int = None):
        groq = GroqChat()
        data = groq.extract_symptoms(text)
        print("Extracted data:", data)
        # Get symptoms
        symptoms = data.get("detected_symptoms") if data else []
        if not symptoms:
            symptoms = [text]  # fallback: todo como un síntoma

        # Extract the duration        
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
            
        severity = self.classify_severity_llm(text, duration_days)

        # Create the entry with all the symptoms
        now = datetime.now().isoformat()
        entry = {
            "timestamp": now,
            "symptoms": data.get("symptoms", []),
            "overall_severity": severity,
            "input_text": text,
        }
        # Save the entry
        self.symptom_manager.add_entry(entry)

        is_urgent = str(severity).lower() == "severe"
        if is_urgent:
            urgent_msg = (
                "🚨 **Potentially urgent symptoms detected.**\n"
                "Please call emergency services or go to the hospital immediately.\n"
                "If you are already in the hospital, inform the medical staff about these symptoms."                
            )            
            return severity, urgent_msg
        
        recommendation_text = ""
        if self.notify_fn:
            recommendation_text = self.notify_fn(text, severity) or ""
        return severity, recommendation_text   
    
    def get_symptom_duration(self, symptom: str) -> int:
        for entry in self.symptom_history:
            if entry["symptom"].lower() == symptom.lower():
                timestamp = datetime.fromisoformat(entry["timestamp"])
                return (datetime.now() - timestamp).days + 1
        return 1
    
