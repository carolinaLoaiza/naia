from datetime import datetime, timedelta
import json
import os
import difflib
from uuid import uuid4
from app.MedicalRecordManager import MedicalRecordManager
from data.DataBaseManager import DatabaseManager

from app.GroqChat import GroqChat

class RecoveryCheckUpScheduleManager:
    def __init__(self, user_id):
        self.user_id = user_id
        db_manager = DatabaseManager()
        self.collection = db_manager.get_collection("routineTracker")
    # def __init__(self, username):        
    #     self.history_file = f"data/history_{username}.json"
    #     self.routine_tracker_file = f"data/routineTracker_{username}.json"

    # def load_medical_record(self):
    #     if not os.path.exists(self.history_file):
    #         return []
    #     with open(self.history_file, "r", encoding="utf-8") as f:
    #         return json.load(f)
        
    # def load_routine_tracker(self):
    #     with open(self.routine_tracker_file, "r", encoding="utf-8") as f:
    #         return json.load(f)
    def load_tracker(self):
        docs = list(self.collection.find({"patient_id": self.user_id}))
        return docs
    
    # def save_routine_tracker(self, tracker):
    #     with open(self.routine_tracker_file, "w", encoding="utf-8") as f:
    #         json.dump(tracker, f, indent=2)
    
    # def save_routine_tracker(self, tracker):
    #     if tracker:
    #         self.collection_tracker.delete_many({"patient_id": self.user_id})
    #         self.collection_tracker.insert_many(tracker)
    def save_checkup(self, checkup_data: dict, flag: bool) -> bool:
        """
        Save a new checkup in the DB
        checkup_data must contain:
        - activity: str
        - date: str 'YYYY-MM-DD'
        - time: str 'HH:MM' o None
        - duration_minutes: int
        - notes: str
        - type: str (ej: "personal")
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
        for record in updated_records:
            record_id = record.get("_id") or record.get("id")  # usar lo que tengas
            if record_id is None:                
                continue  # si no hay id, no actualizamos
            self.collection.update_one(
                {"id": record_id},  # filtro por _id
                {"$set": {"completed": record["completed"]}}
            )
    # def return_routine_info (self):
    #     if os.path.exists(self.routine_tracker_file):
    #         return self.load_routine_tracker()
    #     else:
    #         return self.create_routine_tracker_from_history()
    def return_routine_info(self):
        tracker = self.load_tracker()
        if tracker:
            return tracker
        return self.create_tracker_from_history()
    
    # def create_routine_tracker_from_history(self):
    #     data = self.load_medical_record()
    #     surgery_date_str = data.get("surgery_date", None)
    #     self.start_date = datetime.strptime(surgery_date_str, "%Y-%m-%d") if surgery_date_str else datetime.now()
    #     chat = GroqChat()
    #     routine_items = data.get("post_surgery_recommendations", {}).get("at_home", [])            
    #     routine_text = "\n".join(routine_items) if routine_items else ""
    #     surgery_date_str = data.get("surgery_date", datetime.now().strftime("%Y-%m-%d"))
    #     surgery_date = datetime.strptime(surgery_date_str, "%Y-%m-%d")
    #     routine_schedule_generated = []
    #     if routine_text:
    #         try:
    #             routine_schedule_raw = chat.extract_routine_from_medical_record(routine_text, surgery_date)
    #             routine_schedule_data = json.loads(routine_schedule_raw)
    #             routine_schedule_generated = self.build_schedule_from_extracted_info(routine_schedule_data, surgery_date)                
    #         except Exception as e:
    #             print(f"Error interpreting routine schedule: {e}")
    #             routine_schedule_generated = []
    #     else:
    #         print("No routine text found in medical record.")
    #     self.save_routine_tracker(routine_schedule_generated)       
    #     return routine_schedule_generated
    def create_tracker_from_history(self):
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
            # asignar IDs únicos y patient_id
            for t in tracker_docs:
                t["id"] = str(uuid4())
                t["patient_id"] = self.user_id
            self.collection.insert_many(tracker_docs)
        return tracker_docs
    
    def build_schedule_from_extracted_info(self, info_list, surgery_date):
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
        now = datetime.now()
        start = now - timedelta(minutes=window_minutes)
        end = now + timedelta(minutes=window_minutes)
        tracker = self.load_tracker()
        upcoming = []
        for task in tracker:
            # Ignorar tareas ya completadas o las que no tienen hora (ongoing)
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
        chat = GroqChat()
        tracker = self.load_tracker()
        if not tracker:
            return None, None
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        # Filtrar solo tareas de hoy ± 1 horas
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
