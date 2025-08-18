import os
import json
from datetime import datetime
from typing import List, Dict, Optional

import requests

class MedicalRecordManager:
    """
    Class for managing and accessing a patient's medical record from a mock NHS API.

    Attributes:
        username (str): The patient ID or username used to fetch the record.
        api_url (str): Base URL of the mock NHS API.
        record (dict): Loaded medical record for the patient.

    Methods:
        load_record() -> dict:
            Fetches the patient's medical record from the API.
            Returns the record as a dictionary, or None if not found or on error.
        
        get_patient_info() -> dict:
            Returns a simplified dictionary of the patient's basic information:
            - patient_id
            - name
            - age
            - gender
            - phone
            - location
    """
    def __init__(self, username: str):
        self.username = username
        self.api_url = "https://689c738058a27b18087e39e2.mockapi.io/mock_nhs_api/v1/patients"
        self.record = self.load_record()

    def load_record(self) -> dict:
        try:
            response = requests.get(f"{self.api_url}?patient_id={self.username}")
            response.raise_for_status()
            data = response.json()
            if not data:
                print(f"No medical history found for user '{self.username}' in API")
                return None
            return data[0]
        except Exception as e:
            print(f"Error loading medical record from NHS MockAPI: {e}")
            return None
 
    def get_patient_info(self) -> dict:
        return {
            "patient_id": self.record.get("patient_id"),
            "name": self.record.get("name"),
            "age": self.record.get("age"),
            "gender": self.record.get("gender"),
            "phone": self.record.get("phone"),
            "location": self.record.get("location", {}),
        }

    # Surgery info
    def get_surgery_info(self) -> dict:
        return {
            "surgery": self.record.get("surgery"),
            "surgery_date": self.record.get("surgery_date"),
            "post_surgery_recommendations": self.record.get("post_surgery_recommendations", {})
        }

    # Medications & prescription
    def get_medications(self) -> List[dict]:
        return self.record.get("medications", [])

    def get_prescription_instructions(self) -> List[str]:
        return self.record.get("prescription", {}).get("instructions", [])

    def get_prescription_refill_policy(self) -> str:
        return self.record.get("prescription", {}).get("refill_policy", "")

    # Conditions & history
    def get_pre_existing_conditions(self) -> List[dict]:
        return self.record.get("pre_existing_conditions", [])

    def get_past_medical_history(self) -> List[dict]:
        return self.record.get("past_medical_history", [])

    def get_family_history(self) -> List[dict]:
        return self.record.get("family_history", [])

    # Allergies
    def get_allergies(self) -> List[str]:
        return self.record.get("allergies", [])

    # Immunizations
    def get_immunizations(self) -> List[dict]:
        return self.record.get("immunizations", [])

    # Social history
    def get_social_history(self) -> dict:
        return self.record.get("social_history", {})

    # Follow up appointments
    def get_follow_up_appointments(self) -> List[dict]:
        return self.record.get("follow_up_appointments", [])

    # Notes
    def get_notes(self) -> str:
        return self.record.get("notes", "")