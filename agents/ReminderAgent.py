import os
import json
from datetime import datetime, timedelta
from app.GroqChat import GroqChat
from app.MedicationScheduleManager import MedicationScheduleManager
from app.RecoveryCheckUpScheduleManager import RecoveryCheckUpScheduleManager


def handle_reminder_medication_query(state):
    user_input = state["input"]
    username = state.get("username", "user1")  # default fallback
    medicationScheduleManager = MedicationScheduleManager(username)
    tracker = medicationScheduleManager.load_tracker()
    if not tracker:
        return {"output": "There is no medication data available to display."}
    today_str = datetime.now().strftime("%Y-%m-%d")
    tracker_today = [t for t in tracker if t.get("date") == today_str]
    chat = GroqChat()
    taken_med = chat.extract_taken_medication(user_input)
    if taken_med != "none":
        updated, already_taken = medicationScheduleManager.mark_medication_as_taken(taken_med)
        if updated:
            return {"output": f"✅ Got it! I've marked **{taken_med}** as taken."}
        elif already_taken:
            return {"output": f"📌 Noted! You've already marked **{taken_med}** as taken earlier."}
        else:
            return {"output": f"⚠️ I understood you took **{taken_med}**, but couldn't find it in your schedule."}
    keywords = ["take medicine", "take my meds", "medication", "meds", "reminder", "medication schedule",
    "pill", "pills", "medicine time", "what medicine", "what meds", "when do i take",
    "pending medication", "missed dose", "medicine due", "medicine pending",
    "did i take", "track medication", "medication tracker", "medicine reminder"]
    if any(word in user_input.lower() for word in keywords):
        response = chat.answer_medication_question(user_input, tracker_today)
        return {"output": response}
    return {
        "output": f"📌 Reminder not recognized, but I'll save it as a note: '{user_input}'"
    }

def handle_reminder_recovery_query(state):
    user_input = state["input"]
    username = state.get("username", "user1")    
    recoveryManager = RecoveryCheckUpScheduleManager(username)
    tracker = recoveryManager.load_routine_tracker()
    if not tracker:
        return {"output": "There are no recovery tasks scheduled."}    
    today_str = datetime.now().strftime("%Y-%m-%d")
    tracker_today = [t for t in tracker if t.get("date") == today_str]
    chat = GroqChat()
    done_task = chat.extract_completed_recovery_task(user_input)
    if done_task != "none":
        print("done task", done_task)
        updated, already_done = recoveryManager.mark_task_as_done(done_task)
        if updated:
            return {"output": f"✅ Got it! I've marked **{done_task}** as done."}
        elif already_done:
            return {"output": f"📌 You already marked **{done_task}** as done earlier."}
        else:
            return {"output": f"⚠️ I understood you did **{done_task}**, but couldn't find it in your schedule."}
    is_recovery_related = chat.is_recovery_related(user_input, tracker_today)
    if is_recovery_related:
        response = chat.answer_recovery_question(user_input, tracker_today)
        return {"output": response}
    return {
        "output": f"📌 Recovery request not recognized, but I'll save it as a note: '{user_input}'"
    }
