from datetime import datetime, timedelta
import json
import os
from datetime import datetime, timedelta, time

class MedicationScheduleManager:
    
    def __init__(self, username):
        self.history_file = f"data/history_{username}.json"
        self.tracker_file = f"data/medicationTracker_{username}.json"

    def load_tracker(self):
        if not os.path.exists(self.tracker_file):
            return []
        with open(self.tracker_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def check_pending_medications(self, window_minutes=30):
        now = datetime.now()
        start = now - timedelta(minutes=window_minutes)
        end = now + timedelta(minutes=window_minutes)
        tracker = self.load_tracker()
        upcoming = []
        for med in tracker:
            if med.get("taken"):
                continue
            dt_str = f"{med['date']} {med['time']}"
            try:
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                if start <= dt <= end:
                    upcoming.append(f"- 💊 {med['med_name']} ({med['dose']}) a las {med['time']}")
            except:
                continue
        return upcoming
    
    def mark_medication_as_taken_deprecated(self, med_name):
        tracker = self.load_tracker()
        found = False
        already_taken = False
        for entry in tracker:
            if entry["med_name"].lower() == med_name.lower():
                if entry.get("taken"):
                    already_taken = True
                    continue
                entry["taken"] = True
                found = True
                break
        if found:
            self.save_tracker(tracker)
            return True, False
        return False, already_taken

    def mark_medication_as_taken(self, user_input: str):
        tracker = self.load_tracker()
        if not tracker:
            return None, None
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        window_minutes = 30
        meds_today = []
        # Filtrar medicinas de hoy que no estén tomadas y dentro de la ventana temporal
        for entry in tracker:
            if entry.get("date") != today_str or entry.get("taken"):
                continue
            try:
                med_time = datetime.strptime(f"{entry['date']} {entry['time']}", "%Y-%m-%d %H:%M")
            except:
                continue
            if abs((med_time - now).total_seconds()) <= window_minutes * 60:
                meds_today.append(entry)
        if not meds_today:
            return None, None
        # Buscar en meds_today la medicina cuyo nombre esté en user_input (ignorar mayúsculas)
        user_input_lower = user_input.lower()
        for med in meds_today:
            if med["med_name"].lower() in user_input_lower:
                if med.get("taken"):
                    return None, True
                med["taken"] = True
                self.save_tracker(tracker)
                return med["med_name"], False
        # Si no encontró ninguna coincidencia en la ventana temporal
        return None, False


    def load_medical_record(self):
        if not os.path.exists(self.history_file):
            return []
        with open(self.history_file, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def save_tracker(self, tracker):
        with open(self.tracker_file, "w", encoding="utf-8") as f:
            json.dump(tracker, f, ensure_ascii=False, indent=2)


    def create_tracker_from_history(self):
        data = self.load_medical_record()
        medications = data.get("medications", [])
        surgery_date_str = data.get("surgery_date", None)
        self.start_date = datetime.strptime(surgery_date_str, "%Y-%m-%d") if surgery_date_str else datetime.now()
        frequency_schedule = {
            "6x/day": [time(6, 0), time(10, 0), time(14, 0), time(18, 0), time(22, 0), time(2, 0)],
            "5x/day": [time(7, 0), time(11, 0), time(15, 0), time(19, 0), time(23, 0)],
            "4x/day": [time(8, 0), time(12, 0), time(16, 0), time(20, 0)],
            "3x/day": [time(8, 0), time(14, 0), time(20, 00)],
            "2x/day": [time(9, 0), time(21, 0)],
            "1x/day": [time(9, 0)],
        }
        tracker = []
        for med in medications:
            duration_str = med.get("duration", "7 days")
            days = int(duration_str.split()[0])
            freq = med.get("frequency", "").lower()
            scheduled_times = frequency_schedule.get(freq, [time(9,0)])
            for day_offset in range(days):
                day_date = self.start_date + timedelta(days=day_offset)
                day_str = day_date.strftime("%Y-%m-%d")
                for t in scheduled_times:
                    time_str = t.strftime("%H:%M")
                    tracker.append({
                        "date": day_str,
                        "time": time_str,
                        "med_name": med.get("name"),
                        "dose": med.get("dose"),
                        "frequency": med.get("frequency"),
                        "taken": False
                    })
        self.save_tracker(tracker)
        return tracker

    def return_medication_info (self):
        if os.path.exists(self.tracker_file):
            return self.load_tracker()
        else:
            return self.create_tracker_from_history()


