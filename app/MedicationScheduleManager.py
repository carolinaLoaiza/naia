from datetime import datetime, timedelta

class MedicationScheduleManager:
    def __init__(self, medications, start_date=None):
        """
        medications: list of dicts with keys: name, dose, frequency, duration
        start_date: date from which the medication starts, in "YYYY-MM-DD" format
        """
        self.medications = medications
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now()
        self.schedule = []

    def _parse_frequency(self, freq):
        """
        Converts the frequency in a list of hours of the day (24h) for doses.
        Supports some common formats.
        """
        freq = freq.lower()
        doses_times = []

        if freq == "as needed":
            # no program fixed doses for 'as needed'
            return []

        if "every" in freq and "hours" in freq:
            hours_interval = int(freq.split("every")[1].strip().split(" ")[0])
            # doses every X hours starting at 8:00 AM for example
            current_hour = 8
            while current_hour < 24:
                doses_times.append(current_hour)
                current_hour += hours_interval
        elif "x/day" in freq:
            times_per_day = int(freq.split("x/day")[0].strip())
            # distribute doses evenly between 8am and 10pm (14h)
            interval = 14 / (times_per_day - 1) if times_per_day > 1 else 0
            for i in range(times_per_day):
                dose_hour = 8 + i * interval
                doses_times.append(int(round(dose_hour)))
        elif freq == "1x/day":
            doses_times = [8]  # 8 AM by default
        else:
            # unrecognized frequency, no schedule
            doses_times = []

        return doses_times

    def generate_schedule(self):
        """
        Generates the dosing schedule for all medications.
        For 'ongoing', generates only for 7 days by default.
        """
        schedule = []
        for med in self.medications:
            med_name = med["name"]
            dose = med["dose"]
            freq = med.get("frequency", "").lower()
            duration = med.get("duration", "").lower()

            # Calculate number of days
            if duration == "ongoing":
                days = 7  # generates 7 days by default for ongoing
            else:
                try:
                    days = int(duration.split()[0])  # assumes "5 days", takes 5
                except Exception:
                    days = 1  # by default 1 day if it can't be parsed

            dosis_hours = self._parse_frequency(freq)

            for day_offset in range(days):
                day_date = self.start_date + timedelta(days=day_offset)
                date_str = day_date.strftime("%Y-%m-%d")
                for hour in dosis_hours:
                    time_str = f"{hour:02d}:00"
                    schedule.append({
                        "date": date_str,
                        "time": time_str,
                        "med_name": med_name,
                        "dose": dose,
                        "taken": False
                    })

        self.schedule = schedule
        return schedule

    def get_upcoming_doses(self, minutes_ahead=1):
        """
        Returns two lists:
        - meds_now: meds to take at the current time (HH:MM)
        - meds_soon: meds to take in 'minutes_ahead' minutes
        """
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        current_time_str = now.strftime("%H:%M")
        upcoming_time_str = (now + timedelta(minutes=minutes_ahead)).strftime("%H:%M")

        meds_now = []
        meds_soon = []

        for entry in self.schedule:
            if entry["date"] != today_str or entry["taken"]:
                continue

            if entry["time"] == current_time_str:
                meds_now.append(entry)
            elif entry["time"] == upcoming_time_str:
                meds_soon.append(entry)

        return meds_now, meds_soon

    def mark_as_taken(self, med_name, date_str, time_str):
        """
        Marks a specific medication dose as taken
        """
        for entry in self.schedule:
            if (entry["med_name"] == med_name and
                entry["date"] == date_str and
                entry["time"] == time_str):
                entry["taken"] = True
                return True
        return False
