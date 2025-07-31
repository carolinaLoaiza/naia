import json
import re
from dotenv import load_dotenv
from pathlib import Path
import streamlit as st
#load_dotenv() 

import os
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq

class GroqChat:
    def __init__(self):
        self.api_key = st.secrets["GROQ_API_KEY"]
        self.llm = ChatGroq(groq_api_key=self.api_key, temperature=0.5, model="llama-3.1-8b-instant")
         # Modelo para todo (puedes cambiarlo luego si quieres separar)
        self.chat_llm = ChatGroq(groq_api_key=self.api_key
                                 , temperature=0.4
                                 , model="llama-3.1-8b-instant")
        
        self.classifier_llm = ChatGroq(groq_api_key=self.api_key
                                       , temperature=0.0
                                       , model="llama-3.1-8b-instant")

    def get_initial_messages(self):
        return [
            SystemMessage(content="You are a helpful assistant for post-surgery recovery.")
        ]

    def human_message(self, content):
        return HumanMessage(content=content)

    def ai_message(self, content):
        return AIMessage(content=content)    
        
    def get_response(self, messages):
        return self.chat_llm.invoke(messages).content 

    # This method is used to get a response from the chat model if the request does no suit with any of the classification intent
    def get_chat_response(self, user_input: str) -> str:
        messages = self.get_initial_messages()
        messages.append(self.human_message(user_input))
        return self.get_response(messages)    
    
    def classify_intent(self, user_input: str) -> str:
        prompt = f"""
        You are an intent classifier for a post-surgery assistant.

        Given the user's input, respond with ONLY one of the following:
        - health_agent
        - reminder_agent
        - chat_agent

        User: "{user_input}"
        """
        
        response = self.classifier_llm.invoke([HumanMessage(content=prompt)]).content.strip().lower()
        return response

    def extract_symptoms(self, user_input):

        prompt = f"""
            Extract symptoms and metadata from the user's message.
            Return ONLY ONE raw JSON object. No Markdown, no comments, no extra text.
            - overall_severity: one of "mild", "moderate", "severe", or "unknown"
            - symptoms: array of objects with fields:
                - name (string)
                - location (string or null)
                - duration_days (integer or null)
                - severity (one of "mild","moderate","severe" or null)
                - onset (string or null)

            Respond with JSON only.

            Rules:
            - overall_severity must be exactly: mild, moderate, severe, or unknown.
            - Provide per-symptom duration ONLY as duration_days (integer). If unknown, use null.
            - "location" must be anatomical (e.g., "head", "left arm").
            - If no symptoms are found, return "symptoms": [] and set "overall_severity": "unknown".

            User text: "{user_input}"
            """
        
        response = self.chat_llm.invoke([HumanMessage(content=prompt)]).content.strip()
        print("Prompt for symptom extraction:", response)
        try:
            start = response.find("{")
            end   = response.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise ValueError("No JSON object found in response.")
            json_text = response[start:end+1]
            json_text = (
                json_text
                .replace("\u00A0", " ")  # NBSP
                .replace("\u200B", "")   # zero-width space
                .replace("“", '"').replace("”", '"').replace("’", "'")  # comillas tipográficas
            )
            print("JSON text extracted:", json_text)
            data = json.loads(json_text)
            return data
        except Exception as e:
            print("JSON parse error:", e)
            print("Raw model response:", response)  # <-- usa 'response', no 's'
            return {}

    def extract_duration_from_text(self, text: str, symptom: str) -> int:
        prompt = f"""
        The following user message might mention how many days they have had this symptom: {symptom}.
        Extract the number of days (as an integer). If not mentioned, respond with 0.

        Message:
        \"\"\"{text}\"\"\"

        Answer with only a number.
        """
        response = self.classifier_llm.invoke([HumanMessage(content=prompt)]).content.strip()
        try:
            duration = int(response.strip())
            return max(duration, 0)
        except ValueError:
            return 0

    def classify_severity(self, symptom: str, patient_context: dict, duration_days: int) -> str:
        prompt = f"""
        You are a post-surgery symptom triage assistant.

        Patient context:
        - Surgery: {patient_context.get('surgery')}
        - Duration of symptom: {duration_days} days
        - Medications: {', '.join([med['name'] for med in patient_context.get('medications', [])])}
        - Pre-existing conditions: {', '.join([cond['name'] for cond in patient_context.get('pre_existing_conditions', [])])}

        Evaluate the severity of the symptom: "{symptom}"

        Classify it as one of: "mild", "moderate", "severe".

        Respond only with the severity.
        """
        response = self.classifier_llm.invoke([HumanMessage(content=prompt)]).content.strip()
        return response.lower()