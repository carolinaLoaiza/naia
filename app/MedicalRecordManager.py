import os
import json
from datetime import datetime
from typing import List, Dict, Optional

class MedicalRecordManager:
    def __init__(self, username: str, base_path: str = "data/"):
        self.username = username
        self.file_path = os.path.join(base_path, f"history_{username.lower()}.json")
        self.record = self.load_record()

    def load_record(self) -> dict:
        if not os.path.exists(self.file_path):
            print(f"No medical history found for user '{self.username}' at {self.file_path}")
            return None        
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading medical record: {e}")
            return None

    def save_record(self) -> None:
        with open(self.file_path, "w") as f:
            json.dump(self.record, f, indent=2)

    # Basic info
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

    def update_prescription(self, instructions: List[str], refill_policy: str) -> None:
        self.record["prescription"] = {
            "instructions": instructions,
            "refill_policy": refill_policy
        }
        self.save_record()

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

    # Sample of simple update: adding a note
    def add_note(self, note: str) -> None:
        existing_notes = self.record.get("notes", "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        updated_notes = existing_notes + f"\n[{timestamp}] {note}"
        self.record["notes"] = updated_notes.strip()
        self.save_record()
