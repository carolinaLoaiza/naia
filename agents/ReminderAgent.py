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
    all_reminders = recoveryManager.load_routine_tracker()
    chat = GroqChat()
    referenced_reminder = chat.find_reminder_mentioned(user_input, all_reminders)
    
    if referenced_reminder == "none":
        return {"output": "This message doesn't seem related to any reminders."}
    else:
        action, *reminder_name_parts = referenced_reminder.split("|")
        reminder_name = reminder_name_parts[0] if reminder_name_parts else None
        print ("action --------------", action)
        if action == "consult_existing":
            print(f"User wants to consult about reminder: {reminder_name}")
            if not all_reminders:
                return {"output": "There are no recovery tasks scheduled."}    
            today_str = datetime.now().strftime("%Y-%m-%d")
            tracker_today = [t for t in all_reminders if t.get("date") == today_str]
            is_recovery_related = chat.is_recovery_related(user_input, tracker_today)
            if is_recovery_related:
                response = chat.answer_recovery_question(user_input, tracker_today)
                return {"output": response}            
        elif action == "mark_done_existing":
            print(f"User wants to mark done reminder: {reminder_name}")
            if not all_reminders:
                return {"output": "There are no recovery tasks scheduled."}    
            today_str = datetime.now().strftime("%Y-%m-%d")
            tracker_today = [t for t in all_reminders if t.get("date") == today_str]
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
        elif action == "reminder_crud":
            print("REMINDER CRUD ")
            return handle_crud_reminder(state, all_reminders)
            # Decir que sólo puede modificar los personales
        else:
            return {"output": "This message doesn't seem related to any reminders."}

def handle_crud_reminder (state, all_reminders):
    user_input = state["input"]
    username = state.get("username", "user1")    
    recoveryManager = RecoveryCheckUpScheduleManager(username)
    
    chat = GroqChat()
    classify_reminder = chat.get_reminder_information(user_input, all_reminders)
    print("classify reminder ------------------------------ ", classify_reminder)
    print ("comparison " , "YES|DOCTOR" in classify_reminder)
    if "NO" in classify_reminder:
        json_str = chat.extract_reminder_info_simple(user_input)
        reminder_info = json.loads(json_str)
        date = datetime.today().strftime("%Y-%m-%d")
        activity = reminder_info.get("activity", "").strip().capitalize()
        time_str = reminder_info.get("time")
        frequency_str = reminder_info.get("frequency", "").lower()
        period_str = reminder_info.get("period") or "ongoing"
        all_schedules = recoveryManager.load_routine_tracker()

        all_schedules.append({
                    "activity": activity,
                    "date": date,
                    "time": time_str,
                    "total_days": None,
                    "preferred_times": None,
                    "frequency": frequency_str,
                    "duration_minutes": None,
                    "completed": False,
                    "is_ongoing": True,
                    "notes": "",
                    "type": "personal"
                })
        recoveryManager.save_routine_tracker(all_schedules)
        confirmation_message = (
            f"Your reminder for **\"{activity}\"** has been successfully created.\n\n"
            f"- Date: {date} - {time_str if time_str else 'Not specified'}\n"
            f"- Frequency: {frequency_str if frequency_str else 'Not specified'}\n"
        )
        return {"output": f"⏰ {confirmation_message}"}
    elif "YES|PERSONAL" in classify_reminder:
        return {"output": "📝 This is a personal reminder. What do you want to do — edit, delete, or change its schedule?"}
    elif "YES|DOCTOR" in classify_reminder:
        return {"output": "⚠️ This reminder was set by your doctor and cannot be modified. You can only view it."}
    else:
        return {"output": "Sorry, I couldn't process your request."}

    

def handle_reminder_recovery_doctor(state, referenced_reminder):
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

