from datetime import datetime, timedelta
import os
import json
from uuid import uuid4

from data.DataBaseManager import DatabaseManager

class SymptomManager:
    """
    Manages symptom tracking for a specific patient.

    Attributes:
        user_id (str): The unique identifier of the patient.
        collection: MongoDB collection object for storing symptom entries.
    """
    def __init__(self, user_id):
        """
        Initializes a SymptomManager for a specific user.

        Args:
            user_id (str): Unique identifier of the patient.
        """
        self.user_id = user_id
        db_manager = DatabaseManager()
        self.collection = db_manager.get_collection("symptomTracker")    

    def add_entry(self, entry):
        """
        Adds a symptom record to the database with a timestamp.

        Args:
            entry (dict): A dictionary containing symptom data. If 'timestamp' is
                          not present, it will be automatically added.

        Returns:
            dict: The stored entry with added 'timestamp', 'patient_id', and unique 'id'.
        """
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().isoformat()
        entry["patient_id"] = self.user_id
        entry["id"] = str(uuid4())
        self.collection.insert_one(entry)
        return entry

    def add(self, new_symptoms):
        """
        Adds new symptoms to the patient's symptom list if not already present.
        
        Args:
            new_symptoms (list): List of symptom names to add.

        Notes:
            - Requires `self.symptoms` attribute to exist.
            - Saves the updated symptom list by calling self.save().
        """
        for s in new_symptoms:
            if s not in self.symptoms:
                self.symptoms.append(s)
        self.save()

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