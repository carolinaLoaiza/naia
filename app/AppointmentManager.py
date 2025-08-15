import json
from datetime import datetime, timedelta
import os
from uuid import uuid4
from app.GroqChat import GroqChat
from app.MedicalRecordManager import MedicalRecordManager
from data.DataBaseManager import DatabaseManager

class AppointmentManager:
    def __init__(self, user_id):
        self.user_id = user_id
        db_manager = DatabaseManager()
        self.collection_tracker = db_manager.get_collection("appointmentTracker")
        
    # def __init__(self, username):
    #     self.appointments = []
    #     self.history_file = f"data/history_{username}.json"
    #     self.appointment_tracker_file = f"data/followupTracker_{username}.json"

    # def load_medical_record(self):
    #     if not os.path.exists(self.history_file):
    #         return []
    #     with open(self.history_file, "r", encoding="utf-8") as f:
    #         return json.load(f)
        
    # def load_appointment_tracker(self):
    #     with open(self.appointment_tracker_file, "r", encoding="utf-8") as f:
    #         return json.load(f)
    def load_appointment_tracker(self):
        docs = list(self.collection_tracker.find({"patient_id": self.user_id}))
        return docs

    # def save_appointment_tracker(self, tracker):
    #     with open(self.appointment_tracker_file, "w", encoding="utf-8") as f:
    #         json.dump(tracker, f, indent=2)

    def save_appointment_tracker(self, tracker):
        if tracker:
            self.collection_tracker.delete_many({"patient_id": self.user_id})
            self.collection_tracker.insert_many(tracker)
    
    # def return_appointment_info (self):
    #     if os.path.exists(self.appointment_tracker_file):
    #         return self.load_appointment_tracker()
    #     else:
    #         return self.create_followup_tracker_from_history()
    
    def return_appointment_info(self):
        tracker = self.load_appointment_tracker()
        if tracker:
            return tracker
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

    # def create_followup_tracker_from_history(self):
    #     chat = GroqChat()
    #     data = self.load_medical_record()
        
    #     raw_followups = data.get("follow_up_appointments", [])
    #     if not raw_followups:
    #         print("No follow-up data found in history.")
    #         return []
    #     try:
    #         extracted_raw = chat.extract_followups_from_medical_record(raw_followups)
    #         parsed = json.loads(extracted_raw)
    #     except Exception as e:
    #         print("Error extracting or parsing follow-up appointments:", e)
    #         parsed = []
    #     self.save_appointment_tracker(parsed)
    #     self.appointments = parsed
    #     return parsed
    def create_followup_tracker_from_history(self):
        chat = GroqChat()
        medicalRecordManager = MedicalRecordManager(self.user_id)
        history_data = medicalRecordManager.load_record()        
        raw_followups = history_data.get("follow_up_appointments", [])
        if not raw_followups:
            print("No follow-up data found in history.")
            return []
        try:
            extracted_raw = chat.extract_followups_from_medical_record(raw_followups)
            parsed = json.loads(extracted_raw)
            for appt in parsed:
                appt["id"] = str(uuid4())
                appt["patient_id"] = self.user_id
            self.save_appointment_tracker(parsed)
            return parsed
        except Exception as e:
            print("Error extracting or parsing follow-up appointments:", e)
            return []

    # def check_upcoming_appointments(self, window_hours=24):
    #     now = datetime.now()
    #     start = now
    #     end = now + timedelta(hours=window_hours)
    #     tracker = self.load_appointment_tracker()
    #     upcoming = []
    #     for appt in tracker:
    #         if appt.get("completed"):  # si quieres omitir citas ya completadas
    #             continue
    #         dt_str = f"{appt['date']} {appt.get('time', '09:00')}"  # si no hay hora, asumimos 9 AM
    #         try:
    #             dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    #             if start <= dt <= end:                    
    #                 location_info = f" at {appt['location']}" if appt.get("location") else ""
    #                 reason = appt.get("reason", "")
    #                 department = appt.get("department", "")
    #                 clinician = appt.get("clinician", "")
    #                 if reason:
    #                     description = reason
    #                 elif department or clinician:
    #                     description = f"{department} with {clinician}".strip()
    #                 else:
    #                     description = "Medical appointment"
    #                 upcoming.append(f"- 📅 {description}{location_info} on {appt['date']} at {dt.strftime('%H:%M')}")    
    #         except Exception as e:
    #             continue
    #     return upcoming
    def check_upcoming_appointments(self, window_hours=24):
        now = datetime.now()
        start = now
        end = now + timedelta(hours=window_hours)
        tracker = self.load_appointment_tracker()
        upcoming = []
        for appt in tracker:
            if appt.get("completed"):
                continue
            dt_str = f"{appt['date']} {appt.get('time', '09:00')}"
            try:
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                if start <= dt <= end:
                    location_info = f" at {appt['location']}" if appt.get("location") else ""
                    reason = appt.get("reason", "")
                    department = appt.get("department", "")
                    clinician = appt.get("clinician", "")
                    if reason:
                        description = reason
                    elif department or clinician:
                        description = f"{department} with {clinician}".strip()
                    else:
                        description = "Medical appointment"
                    upcoming.append(f"- 📅 {description}{location_info} on {appt['date']} at {dt.strftime('%H:%M')}")
            except:
                continue
        return upcoming



    def mark_appointment_as_completed(self, description):
        tracker = self.load_appointment_tracker()
        found = False
        already_completed = False

        for appt in tracker:
            if appt["description"].lower() == description.lower():
                if appt.get("completed"):
                    already_completed = True
                    continue
                appt["completed"] = True
                found = True
                break

        if found:
            self.save_appointment_tracker(tracker)
            return True, False  # (marcada, ya estaba completada=False)
        return False, already_completed





    def mark_as_attended(self, date_str, time_str):
        for entry in self.appointments:
            if entry["date"] == date_str and entry["time"] == time_str:
                entry["attended"] = True
                return True
        return False

