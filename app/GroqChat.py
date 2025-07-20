import json
import re
from dotenv import load_dotenv
from pathlib import Path
#load_dotenv() 

import os
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq

class GroqChat:
    def __init__(self):
        load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
        self.api_key = os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(groq_api_key=self.api_key, temperature=0.5, model="llama-3.1-8b-instant")

    def get_initial_messages(self):
        return [
            SystemMessage(content="You are a helpful assistant for post-surgery recovery.")
        ]

    def human_message(self, content):
        return HumanMessage(content=content)

    def ai_message(self, content):
        return AIMessage(content=content)

    
        
    def get_response(self, messages):
        return self.llm.invoke(messages).content
    
    
    def extract_symptoms(self, user_input):
        prompt = f"""
            Extract the symptoms from the following text, with metadata.
            Return ONLY one raw JSON object, without explanations, alternatives, or markdown formatting, with these fields:
            - detected_symptoms (list of strings)
            - severity (mild, moderate, severe — if mentioned)
            - duration (free text, e.g., "2 days")
            - requires_attention (true if it seems urgent)
            - location (optional)

            User text: "{user_input}"
            """
        response = self.llm.invoke([HumanMessage(content=prompt)]).content.strip()


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

