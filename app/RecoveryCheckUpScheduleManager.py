from datetime import datetime, timedelta
import json
import os
import difflib

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
                    "notes": info.get("notes", "")
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
                            "completed": False
                        })
                else:
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

    def check_pending_routines(self, window_minutes=30):
        now = datetime.now()
        start = now - timedelta(minutes=window_minutes)
        end = now + timedelta(minutes=window_minutes)
        tracker = self.load_routine_tracker()
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

    def mark_task_as_done_deprecated(self, task_name: str):
        tracker = self.load_routine_tracker()
        found = False
        already_done = False        
        for entry in tracker:
            if entry["activity"].strip().lower() == task_name.strip().lower():
                if entry.get("completed"):
                    already_done = True
                    continue
                entry["completed"] = True
                found = True
                break        
        if found:
            self.save_routine_tracker(tracker)
            return True, False  # actualizado, no estaba ya marcado
        return False, already_done  # no encontrado o ya marcado


    def mark_task_as_done(self, user_input: str):
        chat = GroqChat()
        tracker = self.load_routine_tracker()
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
                task["completed"] = True
                self.save_routine_tracker(tracker)
                return task["activity"], False
        return None, False

    def get_tasks_for_day(self, date_str=None):
        """
        Returns tasks scheduled for a specific date.
        Defaults to today.
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        return [t for t in self.schedule if t["date"] == date_str and not t["completed"]]
