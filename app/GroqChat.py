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
                                 , temperature=0.7
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
            Extract the symptoms from the following text, with metadata.
            Return ONLY one raw JSON object, without comments, explanations, alternatives, or markdown formatting, with these fields:
            - detected_symptoms (list of strings)
            - severity (mild, moderate, severe — if mentioned)
            - duration (free text, e.g., "2 days")
            - requires_attention (true if it seems urgent)
            - location (optional)

            User text: "{user_input}"
            """
        response = self.chat_llm.invoke([HumanMessage(content=prompt)]).content.strip()
        try:
        # Match the first JSON object using regex
            json_match = re.search(r'\{.*?\}', response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in response.")

            json_text = json_match.group(0)
            return json.loads(json_text)

        except (json.JSONDecodeError, ValueError) as e:
            print("JSON parse error:", e)
            print("Raw model response:", response)
            return None

