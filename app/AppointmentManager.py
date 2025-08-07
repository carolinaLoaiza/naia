import json
from datetime import datetime
import os
from app.GroqChat import GroqChat

class AppointmentManager:
    def __init__(self, username):
        self.appointments = []
        self.history_file = f"data/history_{username}.json"
        self.appointment_tracker_file = f"data/followupTracker_{username}.json"

    def load_medical_record(self):
        if not os.path.exists(self.history_file):
            return []
        with open(self.history_file, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def load_appointment_tracker(self):
        with open(self.appointment_tracker_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_appointment_tracker(self, tracker):
        with open(self.appointment_tracker_file, "w", encoding="utf-8") as f:
            json.dump(tracker, f, indent=2)
    
    def return_appointment_info (self):
        if os.path.exists(self.appointment_tracker_file):
            return self.load_appointment_tracker()
        else:
            return self.create_followup_tracker_from_history()
    
    def status_with_tristate(self, flag, date_str):        
        today = datetime.now().date()
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        if flag is True:
            return "✅ Yes"
        elif date_obj < today:
            return "❌ No"
        else:
            return "⏳"

    def create_followup_tracker_from_history(self):
        chat = GroqChat()
        data = self.load_medical_record()
        raw_followups = data.get("follow_up_appointments", [])
        if not raw_followups:
            print("No follow-up data found in history.")
            return []
        try:
            extracted_raw = chat.extract_followups_from_medical_record(raw_followups)
            parsed = json.loads(extracted_raw)
        except Exception as e:
            print("Error extracting or parsing follow-up appointments:", e)
            parsed = []
        self.save_appointment_tracker(parsed)
        self.appointments = parsed
        return parsed

    def mark_as_attended(self, date_str, time_str):
        for entry in self.appointments:
            if entry["date"] == date_str and entry["time"] == time_str:
                entry["attended"] = True
                return True
        return False

