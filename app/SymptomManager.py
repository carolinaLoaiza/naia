from datetime import datetime, timedelta
import os
import json

class SymptomManager:
    def __init__(self, user_id, base_path="data/"):
        self.filepath = os.path.join(base_path, f"symptoms_{user_id}.json")
        self.symptoms = self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        return []  # Handle empty file
                    return json.loads(content)
            except (json.JSONDecodeError, IOError):
                return []  # Handle invalid JSON or read errors
        return []
    
    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.symptoms, f, ensure_ascii=False, indent=2)

    
    def add_entry(self, entry):
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().isoformat()
        self.symptoms.append(entry)
        self.save()

    def add(self, new_symptoms):
        for s in new_symptoms:
            if s not in self.symptoms:
                self.symptoms.append(s)
        self.save()

    def get_all(self):
        return self.symptoms

    def filter_recent_symptoms(self, daysDefined):
        cutoff = datetime.now() - timedelta(days=daysDefined)
        recent_symptoms = []
        for entry in self.symptoms:
            try:
                timestamp = datetime.fromisoformat(entry["timestamp"])
                if timestamp >= cutoff:
                    for symptom in entry.get("symptoms", []):
                        if symptom not in recent_symptoms:
                            recent_symptoms.append(symptom)
            except Exception as e:
                print(f"Error parsing entry timestamp: {e}")
                continue
        if not recent_symptoms:
            print("No recent symptoms found.")
            return []       
        return recent_symptoms    