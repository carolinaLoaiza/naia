import json
from datetime import datetime, timedelta
import os
from uuid import uuid4
from app.GroqChat import GroqChat
from app.MedicalRecordManager import MedicalRecordManager
from data.DataBaseManager import DatabaseManager

class AppointmentManager:
    """
    Manages patient appointments, including tracking, reminders, and follow-ups.

    Attributes:
        user_id (str): ID of the patient.
        collection_tracker (pymongo collection): MongoDB collection for appointment tracking.
    """
    def __init__(self, user_id):
        """
        Initializes the AppointmentManager for a given user.

        Args:
            user_id (str): Patient's unique identifier.
        """
        self.user_id = user_id
        db_manager = DatabaseManager()
        self.collection_tracker = db_manager.get_collection("appointmentTracker")
        
    def load_appointment_tracker(self):
        """
        Loads all appointment records for the user from the database.

        Returns:
            list[dict]: List of appointment documents.
        """
        docs = list(self.collection_tracker.find({"patient_id": self.user_id}))
        return docs

    def save_appointment_tracker(self, tracker):
        """
        Saves the user's appointment tracker, replacing any existing records.

        Args:
            tracker (list[dict]): List of appointment records to save.
        """
        if tracker:
            self.collection_tracker.delete_many({"patient_id": self.user_id})
            self.collection_tracker.insert_many(tracker)
   
    def return_appointment_info(self):
        """
        Retrieves appointment tracker; if none exists, generates it from medical history.

        Returns:
            list[dict]: List of appointment records.
        """
        tracker = self.load_appointment_tracker()
        if tracker:
            return tracker
        else:
            return self.create_followup_tracker_from_history()

    def status_with_tristate(self, flag, date_str):
        """
        Returns a visual status for appointments based on completion and date.

        Args:
            flag (bool): True if appointment is completed.
            date_str (str): Appointment date in 'YYYY-MM-DD' format.

        Returns:
            str: "Yes" if completed, "No" if past and not completed, otherwise if upcoming.
        """        
        today = datetime.now().date()
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        if flag is True:
            return "✅ Yes"
        elif date_obj < today:
            return "❌ No"
        else:
            return "⏳"

    def create_followup_tracker_from_history(self):
        """
        Generates follow-up appointment tracker from the patient's medical history.

        Returns:
            list[dict]: List of parsed follow-up appointments.
        """
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

    def check_upcoming_appointments(self, window_hours=24):
        """
        Checks for upcoming appointments within a given time window.

        Args:
            window_hours (int, optional): Time window in hours. Defaults to 24.

        Returns:
            list[str]: Formatted list of upcoming appointments.
        """
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
        """
        Marks an appointment as completed based on its description.

        Args:
            description (str): Description of the appointment.

        Returns:
            tuple[bool, bool]: (marked, already_completed)
                - marked: True if successfully marked.
                - already_completed: True if it was already completed.
        """
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
            # (marked, already completed=False)
            return True, False
        return False, already_completed

    def mark_as_attended(self, date_str, time_str):
        """
        Marks an appointment as attended based on date and time.

        Args:
            date_str (str): Appointment date in 'YYYY-MM-DD' format.
            time_str (str): Appointment time in 'HH:MM' format.

        Returns:
            bool: True if appointment found and marked, else False.
        """
        for entry in self.appointments:
            if entry["date"] == date_str and entry["time"] == time_str:
                entry["attended"] = True
                return True
        return False
    
    def mark_reminder_as_sent(self, date_str, time_str):
        """
        Marks that a reminder has been sent for a specific appointment.

        Args:
            date_str (str): Appointment date in 'YYYY-MM-DD' format.
            time_str (str): Appointment time in 'HH:MM' format.

        Returns:
            bool: True if the database record was updated.
        """
        result = self.collection_tracker.update_one(
            {
                "patient_id": self.user_id,
                "date": date_str,
                "time": time_str
            },
            {"$set": {"reminder_sent": True}}
        )
        if result.modified_count > 0:
            return True
        else:
            return False

