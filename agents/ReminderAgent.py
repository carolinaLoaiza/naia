import os
import json
from datetime import datetime, timedelta
from app.GroqChat import GroqChat
from app.MedicationScheduleManager import MedicationScheduleManager


def handle_reminder_query(state):
    user_input = state["input"]
    username = state.get("username", "user1")  # default fallback
    medicationScheduleManager = MedicationScheduleManager(username)

    tracker = medicationScheduleManager.load_tracker()
    if not tracker:
        return {"output": "There is no medication data available to display."}

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
        response = chat.answer_medication_question(user_input, tracker)
        return {"output": response}
    return {
        "output": f"📌 Reminder not recognized, but I'll save it as a note: '{user_input}'"
    }
