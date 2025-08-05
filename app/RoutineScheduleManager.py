from datetime import datetime, timedelta
import json

from app.GroqChat import GroqChat

class RoutineScheduleManager:
    def __init__(self, routine_items, start_date=None):
        """
        routines: list of dicts with keys:
            - task: description of the activity
            - time_slots: list of "HH:MM" strings
            - duration_days: how many days the routine should last
            - duration_minutes: estimated time spent doing the task
            - category: type of routine (e.g., 'ice', 'exercise', etc.)
        """
        self.routine_items = routine_items
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now()
        self.schedule = []


    def create_routine_tracker_from_history(self, history_path, routine_tracker_path):
        chat = GroqChat()
        with open(history_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        routine_items = data.get("post_surgery_recommendations", {}).get("at_home", [])            
        # Concatenar o formatear como texto para enviar a GPT
        routine_text = "\n".join(routine_items) if routine_items else ""
        print("routine_text ", routine_text)

        surgery_date_str = data.get("surgery_date", datetime.now().strftime("%Y-%m-%d"))
        surgery_date = datetime.strptime(surgery_date_str, "%Y-%m-%d")

        routine_schedule = []
        if routine_text:
            try:
                # Si quieres, podrías modificar la función interpret_routine_with_gpt
                # para que reciba también la fecha inicial y la incluya en el prompt.
                routine_schedule_raw = chat.extract_routine_from_medical_record(routine_text, surgery_date)
                routine_schedule_data = json.loads(routine_schedule_raw)
                routine_schedule_generated = self.build_schedule_from_extracted_info(routine_schedule_data, surgery_date)
                print("routine_schedule generated ", routine_schedule_generated )
            except Exception as e:
                print(f"Error interpreting routine schedule: {e}")
                # fallback o rutina vacía
                routine_schedule_generated = []
        else:
            print("No routine text found in medical record.")

        print("routine_schedule generated x 2", routine_schedule_generated )

        with open(routine_tracker_path, "w", encoding="utf-8") as f:
            json.dump(routine_schedule_generated, f, indent=2)

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
