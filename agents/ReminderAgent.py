import os
import json
from datetime import datetime, timedelta

def load_tracker(username):
    tracker_file = f"data/medicationTracker_{username}.json"
    if not os.path.exists(tracker_file):
        return []
    with open(tracker_file, "r", encoding="utf-8") as f:
        return json.load(f)

def check_pending_medications(tracker, window_minutes=30):
    now = datetime.now()
    start = now - timedelta(minutes=window_minutes)
    end = now + timedelta(minutes=window_minutes)

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

def handle_reminder_query(state):
    user_input = state["input"]
    username = state.get("username", "user1")  # default fallback

    tracker = load_tracker(username)
    if not tracker:
        return {"output": "There is no medication data available to display."}

    keywords = ["take medicine", "take my meds", "medication", "meds", "reminder", "medication schedule",
    "pill", "pills", "medicine time", "what medicine", "what meds", "when do i take",
    "pending medication", "missed dose", "medicine due", "medicine pending",
    "did i take", "track medication", "medication tracker", "medicine reminder"]
    if any(word in user_input.lower() for word in keywords):
        upcoming = check_pending_medications(tracker)
        if upcoming:
            return {
                "output": "You have the following pending medications:\n" + "\n".join(upcoming)
            }
        else:
            return {
                "output": "You don't have any pending medications right now. Great job!"
            }

    return {
        "output": f"📌 Reminder not recognized, but I'll save it as a note: '{user_input}'"
    }
