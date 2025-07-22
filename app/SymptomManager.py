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
        # entry debe ser un dict con metadata
        self.symptoms.append(entry)
        self.save()

    def add(self, new_symptoms):
        for s in new_symptoms:
            if s not in self.symptoms:
                self.symptoms.append(s)
        self.save()

    def get_all(self):
        return self.symptoms