from datetime import datetime
import os
import json
import streamlit as st
from typing import Dict
import requests
from bs4 import BeautifulSoup
from app.GroqChat import GroqChat
from app.SymptomManager import SymptomManager 

groq = GroqChat()

def load_patient_history(username: str) -> dict:
    filename = "history_" + username.lower() + ".json"
    path = os.path.join("data", filename)  
    if not os.path.exists(path):
        raise FileNotFoundError(f"There is no file history for {username}")

    with open(path, "r") as f:
        return json.load(f)

def handle_health_query(state: Dict) -> Dict:
    user_input = state["input"]
    username = st.session_state.get("username")
    try:
        PATIENT_HISTORY = load_patient_history(username)
    except FileNotFoundError as e:
        return {"input": user_input, "output": str(e)}
    
    # Extract symptoms and severity
    symptoms = groq.extract_symptoms(user_input)

    if symptoms is None:
        response = "🩺 I couldn't quite understand your symptoms. Could you please describe them again?"
    else:
        severity = symptoms.get("severity", "moderate").lower()
        symptoms_list = symptoms.get("detected_symptoms", [])
        symptoms = ", ".join(symptoms_list)

        symptomManager = SymptomManager(username, base_path="data/")

        entry = {
            "timestamp": datetime.now().isoformat(),
            "symptoms": symptoms_list,
            "severity": severity,
            "input_text": user_input            
        }
        symptomManager.add_entry(entry)

        if severity in ["severe", "high", "grave"]:
            response = ("🚨 Warning: Your symptoms seem severe. "
                        "Please call emergency services or go to the hospital immediately.")
        else:
            print("PATIENT_HISTORY", PATIENT_HISTORY)
            nhs_context = get_nhs_recommendations(PATIENT_HISTORY["surgery"])
            # Step 3: Build the final prompt for Groq to generate recommendation
            prompt = f"""
                You are a healthcare assistant helping a patient recover from surgery.
                Patient history:
                - gender: {PATIENT_HISTORY['gender']}
                - age: {PATIENT_HISTORY['age']}
                - Surgery: {PATIENT_HISTORY['surgery']}
                - Pre-existing conditions: {PATIENT_HISTORY['pre_existing_conditions']}
                - Past Medical History: {PATIENT_HISTORY['past_medical_history']}
                - Allergies: {PATIENT_HISTORY['allergies']}
                - Social History: {PATIENT_HISTORY['social_history']}
                - Post-surgery recommendation: {PATIENT_HISTORY['post_surgery_recommendations']}
                
                Symptoms reported: {symptoms} (severity: {severity})

                Based on the above and the following NHS official advice:\n\n{nhs_context}\n\n
                Please give a **brief, clear, and empathetic** recovery recommendation to the patient, 
                using simple language and bullet points if needed (3-5 max). Warn urgently if symptoms worsen. 
                End inviting the patient to ask more questions if needed.
                """                            
            recommendation = groq.get_chat_response(prompt)
            response = f"🩺 Based on your condition: {recommendation.strip()}"

    output = response
    reminder = state.get("reminder", "")
    if reminder:
        output = reminder + output
    return {"input": user_input, "output": output}
           

def build_nhs_search_url(surgery_name: str) -> str:
    query = "+".join(surgery_name.lower().split()) 
    return f"https://www.nhs.uk/search/results?q={query}"

def fetch_top_nhs_links(url: str, n: int = 2) -> list[str]:
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.select("a[href^='/recovery/'], a[href^='/complications/']")[:n]
    return ["https://www.nhs.uk" + a["href"] for a in items if a.get("href")]

def fetch_page_text(url: str) -> str:
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    paragraphs = soup.select("article p, article li, article h2")
    return "\n".join(p.get_text() for p in paragraphs)

def get_nhs_recommendations(surgery_name: str, n: int = 2) -> str:
    search_url = build_nhs_search_url(surgery_name)
    links = fetch_top_nhs_links(search_url, n)
    all_text = ""
    for link in links:
        all_text += fetch_page_text(link) + "\n\n"
    truncated = all_text[:4000]  # evita pasar token overflow al modelo
    return truncated

