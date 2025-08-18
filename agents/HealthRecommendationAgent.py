import json
import re
import textwrap
from app.GroqChat import GroqChat
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import streamlit as st
from datetime import datetime

from app.MedicalRecordManager import MedicalRecordManager
from app.SymptomManager import SymptomManager
from app.ChatHistoryManager import ChatHistoryManager

def handle_recommendation_query(state):
    """
    Generates a health recommendation based on user query,
    medical records, recent symptoms, and chat context.
    """    
    user_input = state["input"]
    username = st.session_state["username"]    

    # Build patient record
    medical_record_manager = MedicalRecordManager(username)
    patient_record = {
        "name": medical_record_manager.record.get("name", "Unknown"),
        "gender": medical_record_manager.record.get("gender", "unknown"),
        "age": medical_record_manager.record.get("age", "unknown"),
        "surgery": medical_record_manager.get_surgery_info().get("surgery", ""),
        "pre_existing_conditions": medical_record_manager.get_pre_existing_conditions(),
        "allergies": medical_record_manager.record.get("allergies", []),
        "medications": medical_record_manager.get_medications(),
        "past_medical_history": medical_record_manager.record.get("past_medical_history", ""),
        "social_history": medical_record_manager.record.get("social_history", ""),
    }
    # Get recent symptoms and chat history
    symptom_manager = SymptomManager(username)
    stored_symptoms = symptom_manager.filter_recent_symptoms(3)
    chat_history_manager  = ChatHistoryManager(username)
    chat_context = chat_history_manager.load()

    # Generate recommendation
    agent = HealthRecommendationAgent(patient_record)
    recommendation = agent.generate_recommendation(stored_symptoms, chat_context=chat_context,  user_query=user_input)
    recommendation = f"📋 " + recommendation                
    return {"output": recommendation, "username": username}

def handle_recommendation_query_with_symptoms(state):
    """
    Generates a recommendation including all stored symptoms.
    """
    user_input = state["input"]
    username = st.session_state["username"]
    medical_record_manager = MedicalRecordManager(username)
    patient_record = {
        "name": medical_record_manager.record.get("name", "Unknown"),
        "gender": medical_record_manager.record.get("gender", "unknown"),
        "age": medical_record_manager.record.get("age", "unknown"),
        "surgery": medical_record_manager.get_surgery_info().get("surgery", ""),
        "pre_existing_conditions": medical_record_manager.get_pre_existing_conditions(),
        "allergies": medical_record_manager.record.get("allergies", []),
        "medications": medical_record_manager.get_medications(),
        "past_medical_history": medical_record_manager.record.get("past_medical_history", ""),
        "social_history": medical_record_manager.record.get("social_history", ""),
    }
    # Include all stored symptoms
    symptom_manager = SymptomManager(username)
    stored_symptoms = symptom_manager.get_all()    
    agent = HealthRecommendationAgent(patient_record)
    recommendation = agent.generate_recommendation_with_symptoms(stored_symptoms,  user_query=user_input)
    return {"output": recommendation, "username": username}

class HealthRecommendationAgent:
    """
    Generates health recommendations using patient records,
    symptoms, chat context, and NHS guidelines.
    """
    def __init__(self, patient_record: Dict):
        self.patient_record = patient_record
        self.groq = GroqChat()        

    def build_prompt(self, symptoms: List[Dict], chat_context: Optional[str] = None, user_query = "") -> str:
        """
        Build the prompt with patient context, symptoms, and NHS guidance.
        """
        # Flatten historical symptom records
        flat = []
        for item in symptoms or []:
            if isinstance(item, dict) and "symptoms" in item and isinstance(item["symptoms"], list):
                flat.extend(item["symptoms"])
            else:
                flat.append(item)
        # Patient context
        patient_ctx = {
            "gender": self.patient_record.get("gender", "unknown"),
            "age": self.patient_record.get("age", "unknown"),
            "surgery": self.patient_record.get("surgery", "unknown"),
            "pre_existing_conditions": self.patient_record.get("pre_existing_conditions", []),
            "allergies": self.patient_record.get("allergies", []),
            "medications": self.patient_record.get("medications", []),
            "past_medical_history": self.patient_record.get("past_medical_history", []),
            "social_history": self.patient_record.get("social_history", {}),
        }
        # JSON serialization
        patient_json = json.dumps(patient_ctx, ensure_ascii=False, separators=(",", ":"))
        symptoms_json = json.dumps(flat, ensure_ascii=False, separators=(",", ":"))
        nhs_context = self.get_nhs_recommendations(self.patient_record.get("surgery", ""))
        nhs_ctx = (nhs_context or "")[:4000]
        patient_name = self.patient_record.get("name", "Patient")
        prompt = textwrap.dedent(f"""
            You are a kind and knowledgeable post-operative healthcare assistant.
            You will receive:
            - PATIENT_RECORD_JSON: the patient's medical history and background
            - SYMPTOMS_JSON: recent symptom reports, if any
            - NHS_GUIDELINES: trusted advice for post-surgical care
            The patient may ask general questions about their recovery, wellbeing, or care after surgery.
            Your job:
            - Answer questions clearly, empathetically, and safely.
            - Use ONLY the information in the JSON blocks. If unsure, say so.
            - Never speculate or provide advice that contradicts allergies or existing conditions.
            - If SYMPTOMS_JSON is not empty, consider it as background, but do NOT treat the question as a symptom report.
            PATIENT_RECORD_JSON:
            {patient_json}

            SYMPTOMS_JSON:
            {symptoms_json}

            NHS_GUIDELINES:
            {nhs_ctx}

            Respond to the patient's question based on the above, keeping these rules:
            - Use clear, plain language
            - Be brief and respectful
            - Provide up to 3 bullet points if relevant (start with "- "), or a short paragraph
            - Do NOT include markdown or code blocks
            - Invite the patient to ask more if they have doubts

            Start your answer like this:
            "{patient_name}, I'm happy to help with your question. Here's what I can tell you:"
            """).strip()
        if chat_context:
            prompt += f"\n\nConversation context:\n{chat_context}\n"
        if user_query:
            prompt += f"\n\nThe patient's current question is:\n\"{user_query.strip()}\"\n"
        return prompt
    
    def build_prompt_with_symptoms(self, symptoms: List[Dict], chat_context: Optional[str] = None, user_query = "") -> str:
        """
        Build the prompt with detailed symptoms included.
        """
        # Flatten historical symptom records
        flat = []
        for item in symptoms or []:
            if isinstance(item, dict) and "symptoms" in item and isinstance(item["symptoms"], list):
                flat.extend(item["symptoms"])
            else:
                flat.append(item)

        # Patient context
        patient_ctx = {
            "gender": self.patient_record.get("gender", "unknown"),
            "age": self.patient_record.get("age", "unknown"),
            "surgery": self.patient_record.get("surgery", "unknown"),
            "pre_existing_conditions": self.patient_record.get("pre_existing_conditions", []),
            "allergies": self.patient_record.get("allergies", []),
            "medications": self.patient_record.get("medications", []),
            "past_medical_history": self.patient_record.get("past_medical_history", []),
            "social_history": self.patient_record.get("social_history", {}),
        }

        # JSON serialization
        patient_json = json.dumps(patient_ctx, ensure_ascii=False, separators=(",", ":"))
        symptoms_json = json.dumps(flat, ensure_ascii=False, separators=(",", ":"))
        nhs_context = self.get_nhs_recommendations(self.patient_record.get("surgery", ""))
        nhs_ctx = (nhs_context or "")[:4000]

        patient_name = self.patient_record.get("name", "Patient")
        prompt = textwrap.dedent(f"""
            You are a compassionate healthcare assistant.

            You will receive:
            - PATIENT_RECORD_JSON: structured medical context
            - SYMPTOMS_JSON: list of recent symptoms (objects)

            Use ONLY the information in these JSON blocks. If something is missing, say you don't know.
            Do not invent medications or doses that conflict with allergies or current meds.
            If SYMPTOMS_JSON is empty, provide general post‑operative care advice relevant to the surgery.

            PATIENT_RECORD_JSON:
            {patient_json}

            SYMPTOMS_JSON:
            {symptoms_json}

            Official NHS guidelines relevant to the patient's surgery and condition:
            {nhs_ctx}

            Based on the above information, provide a clear, brief, and empathetic health recommendation for the patient.
            Respond with a short, plain-text recommendation only (no JSON, no code, no Markdown fences). 
            - Use simple language
            - Provide 3-5 bullet points max (each starting with "- ")
            - Warn urgently if symptoms worsen or if emergency care is needed
            - Invite the patient to ask more questions if needed

            Include at the beginning of the response this sentence: 
            {patient_name}, thank you for sharing your symptoms. Here's some guidance:
            
        """).strip()

        if chat_context:
            prompt += f"\n\nConversation context:\n{chat_context}\n"
        if user_query:
            prompt += f"\n\nThe patient's current question is:\n\"{user_query.strip()}\"\n"
        return prompt

    def generate_recommendation_with_symptoms(self, symptoms: List[Dict], chat_context: Optional[str] = None, user_query="") -> str:
        """Generate a recommendation including detailed symptoms."""
        prompt = self.build_prompt_with_symptoms(symptoms, chat_context, user_query)
        response = self.groq.get_chat_response(prompt)
        return response.strip()
    
    def generate_recommendation(self, symptoms: List[Dict], chat_context: Optional[str] = None, user_query="") -> str:
        """Generate a recommendation without including symptom details."""
        prompt = self.build_prompt(symptoms, chat_context, user_query)
        response = self.groq.get_chat_response(prompt)
        return response.strip()

    def build_nhs_search_url(self, surgery_name: str) -> str:
        """Build an NHS search URL for the given surgery."""
        query = "+".join(surgery_name.lower().split())
        return f"https://www.nhs.uk/search/results?q={query}"

    def fetch_top_nhs_links(self, url: str, n: int = 2) -> List[str]:
        """Fetch the top NHS guideline links related to recovery/complications."""
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")        
        anchors = soup.select("a.app-search-results-item")
        keywords = ["recovery", "recover", "complication", "complicate", "problem", "issue", "risk"]        
        urls = []
        for a in anchors:
            href = a.get("href")
            if not href:
                continue
            # Extract final URL if it's a tracking link
            match = re.search(r"url=([^&]+)", href)
            if match:
                clean_path = requests.utils.unquote(match.group(1))
                # Check if the clean path has the expected structure
                if "/tests-and-treatments/" not in clean_path:
                    continue
                full_url = "https://www.nhs.uk" + clean_path
                # Check if any keyword is in the clean URL
                if any(kw in clean_path.lower() for kw in keywords):
                    urls.append(full_url)
            if len(urls) >= n:
                break
        return urls

    def fetch_page_text(self, url: str) -> str:
        """Extract readable text from an NHS page."""
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        paragraphs = soup.select("article p, article li, article h2")
        return "\n".join(p.get_text() for p in paragraphs)

    def get_nhs_recommendations(self, surgery_name: str, n: int = 2) -> str:
        """Retrieve and truncate NHS recommendations for a given surgery."""
        if not surgery_name:
            return "No NHS information available for unknown surgery."
        search_url = self.build_nhs_search_url(surgery_name)
        links = self.fetch_top_nhs_links(search_url, n)
        all_text = ""
        for link in links:
            try:
                all_text += self.fetch_page_text(link) + "\n\n"
            except Exception as e:
                all_text += f"[Error retrieving content from {link}]: {e}\n\n"
        truncated = all_text[:4000]  # Prevent token overflow to the model
        return truncated
