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
        # print("Prompt for symptom extraction:", response)
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
            # print("JSON text extracted:", json_text)
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
    
    def answer_recovery_question(self, user_input: str, recovery_data: list) -> str:
        # Formatea el JSON como string para que el modelo lo procese
        recovery_json_str = json.dumps(recovery_data, indent=2)
        # print("Recovery JSON:", recovery_json_str)
        prompt = f"""
        You are a helpful assistant that helps users manage their post-surgery recovery tasks and schedules.

        Here is the user's recovery routine tracker in JSON format:

        ```json
        {recovery_json_str}
        ```

        Based on this data, answer the user's question below in a clear and helpful tone.
        If a recovery task is scheduled soon, remind the user.
        If no tasks are pending soon, let them know.
        If the data is incomplete, be honest about it.

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

    def extract_completed_recovery_task(self, user_input: str) -> str:
        prompt = f"""
        The user may be confirming that they have completed a recovery task.

        Your task is to extract ONLY the name of the recovery task they say they have done.
        If no recovery task is clearly mentioned, respond with "none".

        Respond with the exact recovery task name or "none".

        User: "{user_input}"
        """
        response = self.classifier_llm.invoke([HumanMessage(content=prompt)]).content.strip()
        return response.lower()
    
    def is_recovery_related(self, user_input, tracker):
        tracker_simplified = [
             {"activity": t["activity"], "time": t["time"]} 
                for t in tracker
            ]
        prompt = f"""
        Given the user's input and the list of scheduled recovery activities, recovery checkups or recovery tasks, 
        determine if the input describes doing or referring to any of the items listed in the recovery activities.

        Recovery activities: {json.dumps(tracker_simplified)}

        User input: "{user_input}"

        Respond ONLY with "yes" or "no".
        """
        response = self.classifier_llm.invoke([HumanMessage(content=prompt)]).content.strip().lower()
        return response == "yes"

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
    

    def extract_followups_from_medical_record (self, followup_list):
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

    def search_for_tasks_to_mark(self, tasks_str: str, user_input: str) -> str:
        prompt = f"""
        These are the recovery tasks scheduled for today near the current time:
        {tasks_str}

        The user said: "{user_input}"

        Your task:
        - Identify which task number from the list above best matches what the user is saying they have completed.
        - If none match, respond with "none".
        - Respond with ONLY the task number or "none".
        """
        response = self.classifier_llm.invoke(prompt).content.strip().lower()
        return response

    def find_reminder_mentioned(self, user_input, all_reminders):
        unique_tasks = {}
        for reminder in all_reminders:
            name = reminder["activity"].lower()
            reminder_type = "personal" if reminder.get("created_by_patient", False) else "doctor"
            if name not in unique_tasks:
                unique_tasks[name] = {
                    "activity": reminder["activity"],
                    "type": reminder_type
                }
        task_list = [f"{data['activity']} ({data['type']})" for data in unique_tasks.values()]
        task_list_str = "\n".join(f"- {data['activity']} ({data['type']})" for data in unique_tasks.values())

        # print("task_list " , task_list)
        # prompt = f"""
        #     You are a reminder intent classification assistant.

        #     Here is a list of existing reminders with their types:
        #     {task_list_str}

        #     User message: "{user_input}"

        #     Task:
        #     - Determine the user's intent regarding reminders.
        #     - There are exactly four possible outcomes:

        #     1. "mark_done_existing" → The user wants to mark an existing reminder as done/completed.
        #     2. "consult_existing" → The user wants to check, view, or ask about an existing reminders.
        #     3. "reminder_crud" → The user wants to create, modify, or delete a reminder.
        #     4. "none" → The message is unrelated to reminders.

        #     Rules:
        #     - If the message contains words like "create", "add", "new", or "set up", assume the action is "reminder_crud".
        #     - If the message describes that the user has already performed one of the listed reminders (even without saying "done" or "complete"), treat it as "mark_done_existing". Examples: "I took my vitamins", "I applied ice to my knee", "I went for my morning walk".
        #     - If the reminder name mentioned is in the list, return the action type above plus the exact reminder name in the format: ACTION|REMINDER_NAME.
        #     - If the reminder name is not in the list and the action is "reminder_crud", respond with: ACTION|new for a new reminder creation.
        #     - If the message has nothing to do with reminders, respond ONLY with: none.
        #     - Do not explain your answer, just output the exact required format.

        #     Examples:
        #     - consult_existing|Take vitamins
        #     - mark_done_existing|Morning exercise
        #     - reminder_crud|Buy milk
        #     - reminder_crud|new  - for messages like "create a new reminder
        #     - none
        #     """
        prompt = f"""
        You are a reminder intent classifier.

        Existing reminders: {task_list_str}
        User message: "{user_input}"

        Decide the intent:
        1. mark_done_existing → The user indicates they already did one of the listed reminders, even if they don't use "done" or "completed". Examples: "I took my vitamins", "I applied ice on my knee", "I did leg stretches", "I went for my walk".
        2. consult_existing → The user is asking to see, check, or know about an existing reminder.
        3. reminder_crud → The user wants to create, modify, or delete a reminder.
        4. none → The message is unrelated to reminders.

        Respond ONLY with one of:
        mark_done_existing
        consult_existing
        reminder_crud
        none
        """
        result = self.classifier_llm.invoke(prompt).content.strip()
        print ("result------------ ", result)

        if result == "none":
            return "none"
        prompt = f"""
        You are a reminder name matcher.

        Existing reminders: {task_list_str}
        User message: "{user_input}"

        Find the single reminder from the list that best matches the message, even if the wording is different.
        Return ONLY the exact reminder name from the list, or "none" if there is no match.
        """
        result2 = self.classifier_llm.invoke(prompt).content.strip()
        print ("result2------------ ", result2)
        return result + "|" + result2
    
    def get_reminder_information(self, user_input, all_reminders):
        unique_tasks = {}
        for reminder in all_reminders:
            name = reminder["activity"].lower()
            reminder_type = reminder["type"]
            if name not in unique_tasks:
                unique_tasks[name] = {
                    "activity": reminder["activity"],
                    "type": reminder_type
                }
            task_lines = [f"- {data['activity']} ({data['type']})" for data in unique_tasks.values()]
            tasks_text = "\n".join(task_lines)
            prompt = f"""
               You are a reminder matching assistant.

                Here is the list of existing reminders with their type:
                {tasks_text}

                User message:
                "{user_input}"

                Task:
                - Check if the reminder activity mentioned in the user's message refers to one in the list above.
                - Consider it a match even if:
                    * Case (upper/lower) is different.
                    * There are plural/singular variations.
                    * There are extra words like "the", "reminder", "task", "my", etc.
                    * There are action verbs like "delete", "remove", "mark", "complete", etc.
                - If the meaning clearly refers to one existing activity, output ONLY: YES|TYPE (TYPE is "personal" or "doctor").
                - If it does not refer to any activity in the list, output ONLY: NO.
                - No explanations. No extra text. No formatting.
                """
        result = self.classifier_llm.invoke(prompt).content.strip().upper()
        print("Match result:", result)
        print ("_________________________________")
        return result

    def get_new_reminder(self, user_input, all_reminders):
        unique_tasks = {}
        for reminder in all_reminders:
            name = reminder["activity"].lower()
            reminder_type = reminder["type"]
            if name not in unique_tasks:
                unique_tasks[name] = {
                    "activity": reminder["activity"],
                    "type": reminder_type
                }

            prompt = f"""
               You are a reminder matching assistant.

                Here is the list of existing reminders with their type:
                {unique_tasks}

                User message:
                "{user_input}"

                Task:
                - Check if the reminder activity mentioned in the user's message refers to one in the list above.
                - Consider it a match even if:
                    * Case (upper/lower) is different.
                    * There are plural/singular variations.
                    * There are extra words like "the", "reminder", "task", "my", etc.
                    * There are action verbs like "delete", "remove", "mark", "complete", etc.
                - If the meaning clearly refers to one existing activity, output ONLY: YES|TYPE (TYPE is "personal" or "doctor").
                - If it does not refer to any activity in the list, output ONLY: NO|.
                - No explanations. No extra text. No formatting.
                """
        result = self.classifier_llm.invoke(prompt).content.strip().upper()
        print("Match result:", result)
        print ("_________________________________")
        return result
    
    def extract_reminder_info_simple(self, user_input):
        prompt = f"""
            You are an assistant that extracts reminder details from a user's message.

            Given the user's message below, extract the following fields as JSON:
            - activity: short name of the activity (e.g., "Apply ice to the knee")
            - frequency_per_day: how many times per day (integer)
            - duration_minutes: how long each session lasts (in minutes) if specified, else null
            - total_days: for how many days (integer) if specified, -1 if not specified
            - preferred_times: list of time strings (["09:00", "15:00"]) or empty if not specified
            - notes: optional clarifications           

            Instructions:
            - Convert all frequency expressions like "every 4 hours", "every 3 hours", etc. into explicit time values starting from 06:00.
            - For example, "every 4 hours" should become ["06:00", "10:00", "14:00", "18:00", "22:00"].
            - Always provide explicit time slots as a list of HH:MM strings in 24-hour format.
            - total days should be 0 if not specified, or if the user says for tomorrow, it should be 1.
                        
            Return ONLY a JSON object with these keys and values. Use null if a field is not specified.

            User message:
            \"\"\"{user_input}\"\"\"

            Respond ONLY with the JSON object. No extra text or explanation.
        """
        response = self.classifier_llm.invoke(prompt).content.strip()
        print("extracting reminder ", response)
        return response