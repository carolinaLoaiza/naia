from datetime import datetime, timedelta
import json
import os

from app.GroqChat import GroqChat

class RecoveryCheckUpScheduleManager:
    def __init__(self, username):        
        self.history_file = f"data/history_{username}.json"
        self.routine_tracker_file = f"data/routineTracker_{username}.json"

    def load_medical_record(self):
        if not os.path.exists(self.history_file):
            return []
        with open(self.history_file, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def load_routine_tracker(self):
        with open(self.routine_tracker_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_routine_tracker(self, tracker):
        with open(self.routine_tracker_file, "w", encoding="utf-8") as f:
            json.dump(tracker, f, indent=2)
    
    def return_routine_info (self):
        if os.path.exists(self.routine_tracker_file):
            return self.load_routine_tracker()
        else:
            return self.create_routine_tracker_from_history()
    
    def create_routine_tracker_from_history(self):
        data = self.load_medical_record()
        surgery_date_str = data.get("surgery_date", None)
        self.start_date = datetime.strptime(surgery_date_str, "%Y-%m-%d") if surgery_date_str else datetime.now()
        chat = GroqChat()

        routine_items = data.get("post_surgery_recommendations", {}).get("at_home", [])            
        routine_text = "\n".join(routine_items) if routine_items else ""

        surgery_date_str = data.get("surgery_date", datetime.now().strftime("%Y-%m-%d"))
        surgery_date = datetime.strptime(surgery_date_str, "%Y-%m-%d")

        routine_schedule_generated = []
        if routine_text:
            try:
                routine_schedule_raw = chat.extract_routine_from_medical_record(routine_text, surgery_date)
                routine_schedule_data = json.loads(routine_schedule_raw)
                routine_schedule_generated = self.build_schedule_from_extracted_info(routine_schedule_data, surgery_date)
            except Exception as e:
                print(f"Error interpreting routine schedule: {e}")
                routine_schedule_generated = []
        else:
            print("No routine text found in medical record.")
        self.save_routine_tracker(routine_schedule_generated)       
        return routine_schedule_generated

    def build_schedule_from_extracted_info(self, info_list, surgery_date):
        all_schedules = []

        for info in info_list:
            start_date = surgery_date + timedelta(days=info.get("start_offset_days", 0))
            preferred_times = info.get("preferred_times", [])
            frequency = info.get("frequency_per_day", 0)

            for day_offset in range(info["total_days"]):
                date = start_date + timedelta(days=day_offset)

                # Si hay preferred_times, úsalo directamente
                if preferred_times:
                    for time_str in preferred_times:
                        all_schedules.append({
                            "activity": info["activity"],
                            "date": date.strftime("%Y-%m-%d"),
                            "time": time_str,
                            "duration_minutes": info["duration_minutes"],
                            "completed": False
                        })
                else:
                    # Fallback: genera horas distribuidas si no hay preferred_times
                    for i in range(frequency):
                        time_str = f"{9 + i * 5:02d}:00"  # Ej: 09:00, 14:00, 19:00...
                        all_schedules.append({
                            "activity": info["activity"],
                            "date": date.strftime("%Y-%m-%d"),
                            "time": time_str,
                            "duration_minutes": info["duration_minutes"],
                            "completed": False
                        })

        return all_schedules




    def mark_as_completed(self, task, date_str, time_str):
        """
        Marks a specific routine task as completed.
        """
        for entry in self.schedule:
            if (entry["task"] == task and
                entry["date"] == date_str and
                entry["time"] == time_str):
                entry["completed"] = True
                return True
        return False

    def get_tasks_for_day(self, date_str=None):
        """
        Returns tasks scheduled for a specific date.
        Defaults to today.
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        return [t for t in self.schedule if t["date"] == date_str and not t["completed"]]
