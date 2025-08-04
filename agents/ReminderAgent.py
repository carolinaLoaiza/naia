import os
import json
from datetime import datetime, timedelta

from app.GroqChat import GroqChat

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


def mark_medication_as_taken(username, med_name):
    tracker_file = f"data/medicationTracker_{username}.json"
    if not os.path.exists(tracker_file):
        return False

    with open(tracker_file, "r", encoding="utf-8") as f:
        tracker = json.load(f)

    updated = False
    for med in tracker:
        if med.get("taken"):
            continue
        if med.get("med_name", "").lower() == med_name:
            med["taken"] = True
            updated = True
            break

    if updated:
        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(tracker, f, indent=2)
    return updated



def handle_reminder_query(state):
    user_input = state["input"]
    username = state.get("username", "user1")  # default fallback

    tracker = load_tracker(username)
    if not tracker:
        return {"output": "There is no medication data available to display."}


    # 🧠 Nuevo bloque: intenta detectar confirmación de medicamento tomado
    chat = GroqChat()
    taken_med = chat.extract_taken_medication(user_input)

    if taken_med != "none":
        updated = mark_medication_as_taken(username, taken_med)
        if updated:
            return {"output": f"✅ Got it! I've marked **{taken_med}** as taken."}
        else:
            return {"output": f"⚠️ I understood you took **{taken_med}**, but couldn't find it in your schedule."}
        

    keywords = ["take medicine", "take my meds", "medication", "meds", "reminder", "medication schedule",
    "pill", "pills", "medicine time", "what medicine", "what meds", "when do i take",
    "pending medication", "missed dose", "medicine due", "medicine pending",
    "did i take", "track medication", "medication tracker", "medicine reminder"]

    if any(word in user_input.lower() for word in keywords):
        response = chat.answer_medication_question(user_input, tracker)
        return {"output": response}



    return {
        "output": f"📌 Reminder not recognized, but I'll save it as a note: '{user_input}'"
    }
