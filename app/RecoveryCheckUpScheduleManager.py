from datetime import datetime, timedelta
import json
import os
import difflib
from uuid import uuid4
from app.MedicalRecordManager import MedicalRecordManager
from data.DataBaseManager import DatabaseManager

from app.GroqChat import GroqChat

class RecoveryCheckUpScheduleManager:
    """
    Manages the post-surgery recovery check-up and routine schedule for a patient.

    Responsibilities include:
    - Loading and saving routine/check-up entries from/to the database.
    - Creating a recovery routine schedule from medical history.
    - Checking pending routines within a time window.
    - Marking routines as completed based on user input.

    Attributes:
        user_id (str): The ID of the patient.
        collection (pymongo.collection.Collection): The MongoDB collection used to store routines.
    """
    def __init__(self, user_id):
        """
        Initializes the manager with a patient ID and sets up the database collection.

        Args:
            user_id (str): The unique identifier for the patient.
        """
        self.user_id = user_id
        db_manager = DatabaseManager()
        self.collection = db_manager.get_collection("routineTracker")
    
    def load_tracker(self):
        """
        Loads all routine entries for the current patient from the database.

        Returns:
            list[dict]: A list of routine/check-up records for the patient.
        """
        docs = list(self.collection.find({"patient_id": self.user_id}))
        return docs
    
    def save_checkup(self, checkup_data: dict, flag: bool) -> bool:
        """
        Saves a new check-up or routine entry to the database.

        checkup_data (dict): A dictionary containing the checkup/routine details:
                - activity (str): The name of the activity/check-up.
                - date (str): Date in 'YYYY-MM-DD' format. Defaults to today.
                - time (str or None): Scheduled time in 'HH:MM'. Optional.
                - duration_minutes (int): Duration of the activity in minutes.
                - notes (str): Additional notes. Optional.
                - type (str): Type of activity (e.g., 'doctor' or 'personal'). Optional.
                - total_days (int): Total days the activity repeats. Optional.
                - preferred_times (list[str]): Preferred times per day. Optional.
                - frequency (int): Times per day the activity should be done. Optional.
            flag (bool): If True, treat the entry as a doctor-prescribed activity; 
                         otherwise treat as personal.

        Returns:
            bool: True if the entry was successfully inserted into the database; False otherwise.
        """
        if flag:
            doc = {
            "id": str(uuid4()),
            "patient_id": self.user_id,
            "activity": checkup_data.get("activity"),
            "date": checkup_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "time": checkup_data.get("time"),  # puede ser None
            "total_days": checkup_data.get("total_days"),  # puede ser None
            "preferred_times": checkup_data.get("preferred_times"),  # puede ser None
            "frequency": checkup_data.get("frequency", 1),  # puede ser None
            "duration_minutes": checkup_data.get("duration_minutes"),
            "completed": checkup_data.get("completed", False),
            "is_ongoing": checkup_data.get("is_ongoing", True),
            "notes": checkup_data.get("notes", ""),
            "type": checkup_data.get("type", "doctor"),
            "completed": False
            }
        else:
            doc = {
                "id": str(uuid4()),
                "patient_id": self.user_id,
                "activity": checkup_data.get("activity"),
                "date": checkup_data.get("date", datetime.now().strftime("%Y-%m-%d")),
                "time": checkup_data.get("time"),  # puede ser None
                "duration_minutes": checkup_data.get("duration_minutes"),
                "type": checkup_data.get("type", "personal"),
                "completed": False
                }
        result = self.collection.insert_one(doc)
        if result.inserted_id:
            return True
        else:
            return False
        
    def update_completed_status(self, updated_records):
        """
        Updates the 'completed' status of existing routine/check-up entries in the database.

        Args:
            updated_records (list[dict]): List of records with updated 'completed' field.
                Each record must contain 'id' or '_id' to identify the database entry.
        """
        for record in updated_records:
            record_id = record.get("_id") or record.get("id")  
            if record_id is None:                
                continue 
            self.collection.update_one(
                {"id": record_id}, 
                {"$set": {"completed": record["completed"]}}
            )
    
    def return_routine_info(self):
        """
        Retrieves all routine/check-up entries for the patient.
        If none exist, creates a new tracker based on the patient's medical history.

        Returns:
            list[dict]: List of routine/check-up entries.
        """
        tracker = self.load_tracker()
        if tracker:
            return tracker
        return self.create_tracker_from_history()
    
    
    def create_tracker_from_history(self):
        """
        Builds the recovery routine tracker from the patient's medical history.
        Uses GroqChat to parse textual recommendations from the medical record.

        Returns:
            list[dict]: A list of generated routine/check-up entries.
        """
        medicalRecordManager = MedicalRecordManager(self.user_id)
        history_data = medicalRecordManager.load_record()
        if not history_data:
            print("No medical history found to create checkup tracker.")
            return []
        surgery_date_str = history_data.get("surgery_date", None)
        surgery_date = datetime.strptime(surgery_date_str, "%Y-%m-%d") if surgery_date_str else datetime.now()
        chat = GroqChat()
        routine_items = history_data.get("post_surgery_recommendations", {}).get("at_home", [])
        routine_text = "\n".join(routine_items) if routine_items else ""
        tracker_docs = []
        if routine_text:
            try:
                routine_schedule_raw = chat.extract_routine_from_medical_record(routine_text, surgery_date)
                routine_schedule_data = json.loads(routine_schedule_raw)
                tracker_docs = self.build_schedule_from_extracted_info(routine_schedule_data, surgery_date)
            except Exception as e:
                print(f"Error interpreting routine schedule: {e}")
        if tracker_docs:
            # assign unique IDs and patient ID to each entry
            for t in tracker_docs:
                t["id"] = str(uuid4())
                t["patient_id"] = self.user_id
            self.collection.insert_many(tracker_docs)
        return tracker_docs
    
    def build_schedule_from_extracted_info(self, info_list, surgery_date):
        """
        Converts extracted routine information into individual scheduled tasks.

        Args:
            info_list (list[dict]): List of tasks with fields like 'activity', 'start_offset_days',
                                    'preferred_times', 'frequency_per_day', 'total_days'.
            surgery_date (datetime): The surgery date to calculate offsets from.

        Returns:
            list[dict]: List of scheduled routine/check-up entries.
        """
        all_schedules = []
        for info in info_list:
            start_date = surgery_date + timedelta(days=info.get("start_offset_days", 0))
            preferred_times = info.get("preferred_times", [])
            frequency = info.get("frequency_per_day", 0)
            total_days = info.get("total_days", 0)
            # Extract the no temporal tasks
            if ((frequency == 0 and not preferred_times) 
                or ( frequency == 0 and total_days == 0)
                or (not preferred_times and total_days == 0)):
                all_schedules.append({
                    "activity": info["activity"],
                    "date": start_date.strftime("%Y-%m-%d"),
                    "time": None,
                    "total_days": total_days,
                    "preferred_times": preferred_times,
                    "frequency": frequency,
                    "duration_minutes": info.get("duration_minutes", 0),
                    "completed": False,
                    "is_ongoing": True,
                    "notes": info.get("notes", ""),
                    "type": "doctor" 
                })
                continue
            # Extract the scheduled tasks
            for day_offset in range(total_days):
                date = start_date + timedelta(days=day_offset)
                if preferred_times:
                    for time_str in preferred_times:
                        all_schedules.append({
                            "activity": info["activity"],
                            "date": date.strftime("%Y-%m-%d"),
                            "time": time_str,
                            "duration_minutes": info["duration_minutes"],
                            "completed": False,
                            "type": "doctor" 
                        })
                else:
                    for i in range(frequency):
                        time_str = f"{9 + i * 5:02d}:00"  # Ej: 09:00, 14:00, 19:00...
                        all_schedules.append({
                            "activity": info["activity"],
                            "date": date.strftime("%Y-%m-%d"),
                            "time": time_str,
                            "duration_minutes": info["duration_minutes"],
                            "completed": False,
                            "type": "doctor" 
                        })
        return all_schedules

    def check_pending_routines(self, window_minutes=30):
        """
        Checks for routines scheduled within a ±window around the current time.

        Args:
            window_minutes (int): Minutes before/after current time to check.

        Returns:
            list[str]: List of upcoming routines formatted as readable strings.
        """
        now = datetime.now()
        start = now - timedelta(minutes=window_minutes)
        end = now + timedelta(minutes=window_minutes)
        tracker = self.load_tracker()
        upcoming = []
        for task in tracker:
            # Ignore completed tasks or those without a time (ongoing)
            if task.get("completed") or not task.get("time"):
                continue
            dt_str = f"{task['date']} {task['time']}"
            try:
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                if start <= dt <= end:
                    duration_info = f" ({task['duration_minutes']} min)" if task.get("duration_minutes") else ""
                    upcoming.append(f"- 📝 {task['activity']}{duration_info} a las {task['time']}")
            except:
                continue
        return upcoming

    def mark_task_as_done(self, user_input: str):
        """
        Marks a routine task as completed based on user input and time proximity.
        Args: user_input (str): Text input from the user indicating which task was completed.
        Returns: tuple[str or None, bool or None]: 
                - Name of the completed task, or None if none matched.
                - Boolean indicating whether the task was already completed, or None.
        """
        chat = GroqChat()
        tracker = self.load_tracker()
        if not tracker:
            return None, None
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        # Filter only today's tasks ± 1 hours
        tasks_today = []
        for entry in tracker:
            if entry.get("date") != today_str:
                continue
            try:
                task_time = datetime.strptime(f"{entry['date']} {entry['time']}", "%Y-%m-%d %H:%M")
            except:
                continue
            if abs((task_time - now).total_seconds()) <= 1800:  # 1 horas
                tasks_today.append(entry)
        if not tasks_today:
            return None, None
        task_list_str = "\n".join(
            [f"{i+1}. {t['activity']}" for i, t in enumerate(tasks_today)]
        )
        resp = chat.search_for_tasks_to_mark(task_list_str, user_input)
        if resp.isdigit():
            idx = int(resp) - 1
            if 0 <= idx < len(tasks_today):
                task = tasks_today[idx]
                if task.get("completed"):
                    return None, True  # ya estaba hecha
                self.collection.update_one({"id": task["id"]}, {"$set": {"completed": True}})
                # task["completed"] = True
                # self.save_routine_tracker(tracker)
                return task["activity"], False
        return None, False
