from datetime import datetime, timedelta
import os
import json
from uuid import uuid4

from data.DataBaseManager import DatabaseManager

class SymptomManager:
    def __init__(self, user_id):
        self.user_id = user_id
        db_manager = DatabaseManager()
        self.collection = db_manager.get_collection("symptomTracker")    

    def add_entry(self, entry):
        """Agrega un registro de síntomas con timestamp."""
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().isoformat()
        entry["patient_id"] = self.user_id
        entry["id"] = str(uuid4())
        self.collection.insert_one(entry)
        return entry

    def add(self, new_symptoms):
        for s in new_symptoms:
            if s not in self.symptoms:
                self.symptoms.append(s)
        self.save()

    # def get_all(self):
    #     return self.symptoms
    def get_all(self):
        """Return all the records from the patient."""
        return list(self.collection.find({"patient_id": self.user_id}))
    
    def filter_recent_symptoms(self, daysDefined):
        """Filter symptoms recent according to the range of days."""
        cutoff = datetime.now() - timedelta(days=daysDefined)
        cutoff_str = cutoff.isoformat()

        cursor = self.collection.find({
            "patient_id": self.user_id,
            "timestamp": {"$gte": cutoff_str}
        })

        recent_symptoms = []
        for entry in cursor:
            for symptom in entry.get("symptoms", []):
                if symptom not in recent_symptoms:
                    recent_symptoms.append(symptom)

        return recent_symptoms