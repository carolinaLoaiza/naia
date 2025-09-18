from datetime import datetime, timedelta
import json
import os
from datetime import datetime, timedelta, time
from uuid import uuid4
from zoneinfo import ZoneInfo
from app.MedicalRecordManager import MedicalRecordManager
from data.DataBaseManager import DatabaseManager

class MedicationScheduleManager:
    """
    Manages a patient's medication schedule, including tracking doses,
    checking pending medications, marking them as taken, and creating
    trackers from medical history.
    """

    def __init__(self, user_id):
        """
        Initialize the manager for a specific user.

        Args:
            user_id (str): The ID of the patient.
        """
        self.user_id = user_id
        db_manager = DatabaseManager()
        self.collection = db_manager.get_collection("medicationTracker")

    def load_tracker(self):
        """
        Load all medication tracking records for the user.

        Returns:
            list: A list of medication tracker documents.
        """
        docs = list(self.collection.find({"patient_id": self.user_id}))
        return docs
    
    def check_pending_medications(self, window_minutes=30):
        """
        Check for medications that are scheduled within a given time window
        around the current time and have not been taken yet.

        Args:
            window_minutes (int): Time window in minutes to look for upcoming doses.

        Returns:
            list: Formatted list of upcoming medications within the time window.
        """
        zn = ZoneInfo("Europe/London")
        now = datetime.now(zn)
        start = now - timedelta(minutes=window_minutes)
        end = now + timedelta(minutes=window_minutes)
        tracker = self.load_tracker()
        upcoming = []
        for med in tracker:
            if med.get("taken"):
                continue
            dt_str = f"{med['date']} {med['time']}"
            try:
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M").replace(tzinfo=zn)
                if start <= dt <= end:
                    upcoming.append(f"- 💊 {med['med_name']} ({med['dose']}) - {med['time']}")
            except:
                continue
        return upcoming
    
    def mark_medication_as_taken(self, user_input: str):
        """
        Mark a medication as taken if it matches user input and is scheduled
        within a 30-minute window around the current time.

        Args:
            user_input (str): Name or keyword of the medication to mark as taken.

        Returns:
            tuple: (med_name (str) if marked, already_taken (bool))
        """
        zn = ZoneInfo("Europe/London")
        now = datetime.now(zn)
        today_str = now.strftime("%Y-%m-%d")
        window_minutes = 30
        tracker = self.load_tracker()
        meds_today = []
        for med in tracker:
            if med.get("date") != today_str or med.get("taken"):
                continue
            try:
                med_time = datetime.strptime(f"{med['date']} {med['time']}", "%Y-%m-%d %H:%M").replace(tzinfo=zn)
            except:
                continue
            if abs((med_time - now).total_seconds()) <= window_minutes * 60:
                meds_today.append(med)
        if not meds_today:
            return None, None
        user_input_lower = user_input.lower()
        for med in meds_today:
            if med["med_name"].lower() in user_input_lower:
                if med.get("taken"):
                    return None, True
                # Marcar como tomada
                self.collection.update_one(
                    {"id": med["id"]},
                    {"$set": {"taken": True}}
                )
                return med["med_name"], False
        return None, False
    
    def create_tracker_from_history(self):
        """
        Generate a medication tracker from the patient's medical history.

        Returns:
            list: List of created medication tracker documents.
        """
        zn = ZoneInfo("Europe/London")
        medicalRecordManager = MedicalRecordManager(self.user_id)
        history_data = medicalRecordManager.load_record()
        if not history_data:
            print("No medical history found to create medication tracker.")
            return []
        surgery_date_str = history_data.get("surgery_date", None)
        now = datetime.now(zn)
        start_date = datetime.strptime(surgery_date_str, "%Y-%m-%d").replace(zn) if surgery_date_str else now     
        frequency_schedule = {
            "6x/day": [time(6, 0), time(10, 0), time(14, 0), time(18, 0), time(22, 0), time(2, 0)],
            "5x/day": [time(7, 0), time(11, 0), time(15, 0), time(19, 0), time(23, 0)],
            "4x/day": [time(8, 0), time(12, 0), time(16, 0), time(20, 0)],
            "3x/day": [time(8, 0), time(14, 0), time(20, 0)],
            "2x/day": [time(9, 0), time(21, 0)],
            "1x/day": [time(9, 0)],
        }
        tracker_docs = []
        for med in history_data.get("medications", []):
            duration_str = med.get("duration", "7 days")
            days = int(duration_str.split()[0])
            freq = med.get("frequency", "").lower()
            scheduled_times = frequency_schedule.get(freq, [time(9,0)])
            for day_offset in range(days):
                day_date = start_date + timedelta(days=day_offset)
                day_str = day_date.strftime("%Y-%m-%d").replace(tzinfo=zn)
                for t in scheduled_times:
                    time_str = t.strftime("%H:%M").replace(tzinfo=zn)
                    tracker_docs.append({
                         "id": str(uuid4()), 
                        "patient_id": self.user_id,
                        "date": day_str,
                        "time": time_str,
                        "med_name": med.get("name"),
                        "dose": med.get("dose"),
                        "frequency": med.get("frequency"),
                        "taken": False
                    })
        if tracker_docs:
            self.collection.insert_many(tracker_docs)
        return tracker_docs
        
    def return_medication_info(self):
        """
        Retrieve the user's medication records; create tracker from history if none exist.

        Returns:
            list: List of medication tracker documents.
        """
        user_meds = self.load_tracker()    
        if user_meds:
            return user_meds
        else:
            return self.create_tracker_from_history()

    def update_taken_status(self, updated_records):
        """
        Update the 'taken' status of medications in the database.

        Args:
            updated_records (list): List of medication records with updated 'taken' status.
        """
        for record in updated_records:
            record_id = record.get("_id") or record.get("id")  # usar lo que tengas
            if record_id is None:                
                continue  # si no hay id, no actualizamos
            self.collection.update_one(
                {"id": record_id},  # filtro por _id
                {"$set": {"taken": record["taken"]}}
            )