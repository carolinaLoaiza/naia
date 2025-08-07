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
    
    def answer_medication_question(self, user_input: str, medication_data: list) -> str:
        # Formatea el JSON como string para que el modelo lo procese
        medication_json_str = json.dumps(medication_data, indent=2)

        prompt = f"""
        You are a helpful assistant that helps users manage their medication schedules after surgery.

        Here is the user's medication tracker in JSON format:

        ```json
        {medication_json_str}
        ```

        Based on this data, answer the user's question below in a clear and helpful tone. If a medication is due soon, remind the user.
        If no medication is due, let them know. If the data is incomplete, be honest about it.

        User question: "{user_input}"

        Respond in a concise, friendly tone.
        """

        response = self.chat_llm.invoke([HumanMessage(content=prompt)]).content.strip()
        return response
    
    def extract_taken_medication(self, user_input: str) -> str:
        prompt = f"""
        The user may be confirming that they have taken a medication.

        Your task is to extract ONLY the name of the medication they say they have taken.
        If no medication is clearly mentioned, respond with "none".

        Respond with the exact medication name or "none".

        User: "{user_input}"
        """
        response = self.classifier_llm.invoke([HumanMessage(content=prompt)]).content.strip()
        return response.lower()


    def extract_routine_from_medical_record(self, routine_text, surgery_date):
        prompt = f"""
            You are a routine extraction assistant for post-surgical care.

            Given the following doctor's instruction: {routine_text}
            Given this surgery date: {surgery_date},
            
            Please extract ONLY the post-surgical routine activities that specify at least two of three of the following clearly or implicitly:
            - frequency_per_day (times per day, integer greater than zero),
            - duration_minutes (minutes per session, integer greater than zero),
            - total_days (total number of days, integer greater than zero).

            If an instruction lacks two or more of these, exclude it completely from the output.

            Please provide ONLY the JSON array representing the routine schedule.
            Do NOT include any explanations or extra text.
            Return ONLY ONE raw JSON object. No Markdown, no comments, no extra text.
            Return a JSON formatted as:

            Instructions:
            - Convert all frequency expressions like "every 4 hours", "every 3 hours", etc. into explicit time values starting from 06:00.
            - For example, "every 4 hours" should become ["06:00", "10:00", "14:00", "18:00", "22:00"].
            - Always provide explicit time slots as a list of HH:MM strings in 24-hour format.
            - Do NOT include phrases like "every 4 hours" or "as needed" as time values.
            - Ignore any instructions that do not specify frequency, duration per session, and total number of days explicitly or implicitly.
            - Recommendations that only provide general advice without schedule details should be excluded.

            Extract the following fields as JSON:
            - activity: short name of the activity (e.g., "Apply ice to the knee")
            - frequency_per_day: how many times per day (integer)
            - duration_minutes: how long each session lasts (in minutes)
            - total_days: for how many days (integer)
            - start_offset_days: when to start (0 = same day as surgery, 1 = one day after, etc.)
            - preferred_times: list of time strings (["09:00", "15:00"]) or empty if not specified
            - notes: optional clarifications

            Return ONLY ONE valid JSON object. Do not include explanations or formatting.
                       
            """
        response = self.classifier_llm.invoke(prompt).content.strip()
        return response 
    

    def extract_followups_from_medical_record(self, followup_list):
        prompt = f"""
            You are a clinical assistant. Extract detailed follow-up appointment information from the given entries.

            The input is a list of follow-up appointments as found in a patient’s medical record. Some fields may be missing or inconsistent.

            Your task:
            - For **each** appointment, output a standardized object with the following fields:
                - date: in YYYY-MM-DD format
                - time: in HH:MM (24-hour format)
                - department
                - location
                - clinician: name of doctor or specialist
                - reason: short reason for the visit
                - reminder_sent: true/false
                - attended: true/false
                - notes: optional string ("" if none)

            Instructions:
            - Do NOT exclude any appointment, even if some values are missing or empty.
            - Only output a JSON array of cleaned appointments. No Markdown, no explanations, no formatting.

            Follow-up entries:
            {json.dumps(followup_list, indent=2)}
            """          
        response = self.classifier_llm.invoke(prompt).content.strip()
        return response



