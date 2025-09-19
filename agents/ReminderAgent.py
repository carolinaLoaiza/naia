import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.GroqChat import GroqChat
from app.MedicationScheduleManager import MedicationScheduleManager
from app.RecoveryCheckUpScheduleManager import RecoveryCheckUpScheduleManager


def handle_reminder_medication_query(state):
    """
    Handles queries related to medication reminders.
    - Checks today's medication schedule
    - Marks medications as taken
    - Answers medication-related questions

    Args:
        state (dict): Contains "input" (user message) and "username".

    Returns:
        dict: {"output": str} with the assistant's response.
    """
    user_input = state["input"]
    username = state.get("username", "user1")  # default fallback
    medicationScheduleManager = MedicationScheduleManager(username)
    tracker = medicationScheduleManager.load_tracker()
    if not tracker:
        return {"output": "There is no medication data available to display."}
    now = datetime.now(ZoneInfo("Europe/London"))
    today_str = now.strftime("%Y-%m-%d")
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
    """
    Handles queries related to recovery/check-up reminders.
    - Consults existing reminders
    - Marks reminders as done
    - Handles reminder CRUD operations

    Args:
        state (dict): Contains "input" (user message) and "username".

    Returns:
        dict: {"output": str} with the assistant's response.
    """
    user_input = state["input"]
    username = state.get("username", "user1")
    recoveryManager = RecoveryCheckUpScheduleManager(username)
    all_reminders = recoveryManager.load_tracker()
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
            now = datetime.now(ZoneInfo("Europe/London"))  
            today_str = now.strftime("%Y-%m-%d")
            # tracker_today = [t for t in all_reminders if t.get("date") == today_str]

            tracker_today = [
                {k: v for k, v in t.items() if k != "_id"} 
                for t in all_reminders 
                if t.get("date") == today_str
            ]
            is_recovery_related = chat.is_recovery_related(user_input, tracker_today)
            if is_recovery_related:
                response = chat.answer_recovery_question(user_input, tracker_today)
                # print ("responses ", response)
                return {"output": response}   
            else:
                return {"output": f"Reminder not recognized, do you want to create it? Please specify activity, time, period"}        
        elif action == "mark_done_existing":
            print(f"User wants to mark done reminder: {reminder_name}")
            if not all_reminders:
                return {"output": "There are no recovery tasks scheduled."}   
            now = datetime.now(ZoneInfo("Europe/London")) 
            today_str = now.strftime("%Y-%m-%d")
            tracker_today = [t for t in all_reminders if t.get("date") == today_str]
            # done_task = chat.extract_completed_recovery_task(user_input)
            done_task = reminder_name
            print("done_task", done_task)
            if done_task != "none":
                print("done task", done_task)
                updated, already_done = recoveryManager.mark_task_as_done(done_task)
                if updated:
                    return {"output": f"✅ Got it! I've marked **{done_task}** as done."}
                elif already_done:
                    return {"output": f"📌 You already marked **{done_task}** as done earlier."}
                else:
                    return {"output": f"⚠️ I understood you did **{done_task}**, but couldn't find it in your schedule."}
            else:
                    return {"output": f"⚠️ I couldn't find **{done_task}** in your pending tasks."}
        elif action == "reminder_crud":
            return handle_crud_reminder(state, all_reminders)
        else:
            return {"output": "This message doesn't seem related to any reminders."}

def handle_crud_reminder (state, all_reminders):
    """
    Handles CRUD operations (create, update, delete) for recovery reminders.

    Args:
        state (dict): Contains "input" (user message) and "username".
        all_reminders (list): List of current reminders.

    Returns:
        dict: {"output": str} with the assistant's response.
    """
    user_input = state["input"]
    username = state.get("username", "user1")    
    recoveryManager = RecoveryCheckUpScheduleManager(username)
    
    chat = GroqChat()
    classify_reminder = chat.get_reminder_information(user_input, all_reminders)
    print("classify reminder ------------------------------ ", classify_reminder)
    if "NO" in classify_reminder:
        json_str = chat.extract_reminder_info_simple(user_input)
        reminder_info = json.loads(json_str)
        print("reminder info", reminder_info)
        activity = reminder_info.get("activity", "").strip().capitalize()
        frequency_per_day = reminder_info.get("frequency_per_day", 0)
        duration_minutes = reminder_info.get("duration_minutes", 0)
        total_days = reminder_info.get("total_days", 0)
        preferred_times = reminder_info.get("preferred_times", [])
        notes = reminder_info.get("notes", "")
        date = datetime.today()
        # now = datetime.now()
        tz = ZoneInfo("Europe/London")
        now = datetime.now(tz)
        if ((frequency_per_day == 0 and not preferred_times) 
                or ( frequency_per_day == 0 and total_days == 0)
                or (not preferred_times and total_days == 0)):
                new_checkup = {
                    "activity": activity,
                    "date": date.strftime("%Y-%m-%d"),
                    "time": None,
                    "total_days": total_days,
                    "preferred_times": preferred_times,
                    "frequency": frequency_per_day,
                    "duration_minutes": duration_minutes,
                    "completed": False,
                    "is_ongoing": True,
                    "notes": notes,
                    "type": "personal" 
                }
                result = recoveryManager.save_checkup(new_checkup, True)
                if result:
                    confirmation_message = (
                        f"Your reminder for **\"{activity}\"** has been successfully created.\n\n"                       
                    )
                    return {"output": f"⏰ {confirmation_message}"}
                else:
                    return {"output": "⚠️ There was an error creating your reminder. Please try again."}
        else: 
            result = True 
            count = 0
            for i in range(max(total_days + 1, 1)):
                dateTo = date + timedelta(days=i)
                if preferred_times:
                    for time_str in preferred_times:
                        reminder_dt = datetime.strptime(
                            f"{dateTo.strftime('%Y-%m-%d')} {time_str}", "%Y-%m-%d %H:%M"
                        ).replace(tzinfo=tz)                        
                        if reminder_dt <= now:
                            continue
                        new_checkup = {
                            "activity": activity,
                            "date": dateTo.strftime("%Y-%m-%d"),
                            "time": time_str,
                            "duration_minutes": duration_minutes,
                            "completed": False,
                            "type": "personal" 
                        }
                        if recoveryManager.save_checkup(new_checkup, False) == False:
                            result = False
                            break
                        else:
                            count += 1
                else:
                    for j in range(frequency_per_day):
                        time_str = f"{9 + j * 5:02d}:00"  # Ej: 09:00, 14:00, 19:00...
                        reminder_dt = datetime.strptime(
                            f"{dateTo.strftime('%Y-%m-%d')} {time_str}", "%Y-%m-%d %H:%M"
                        ).replace(tzinfo=tz)
                        if reminder_dt <= now:
                            continue
                        new_checkup = {
                            "activity": activity,
                            "date": dateTo.strftime("%Y-%m-%d"),
                            "time": time_str,
                            "duration_minutes": duration_minutes,
                            "completed": False,
                            "type": "personal" 
                        }
                        if recoveryManager.save_checkup(new_checkup, False) == False:
                            result = False
                            break
                        else:
                            count += 1
            if result:
                confirmation_message = (
                    f"Your reminder for **\"{activity}\"** has been successfully created.\n\n"
                    f"- {count} recurrent reminders were created \n"
                    f"- Frequency: {frequency_per_day if frequency_per_day else 'Not specified'}\n"
                )
                return {"output": f"⏰ {confirmation_message}"}
            else:
                return {"output": "⚠️ There was an error creating your reminder. Please try again."}
    elif "YES|PERSONAL" in classify_reminder:
        return {"output": "📝 This is a personal reminder. What do you want to do — create, or delete a reminder?"}
    
    elif "YES|DOCTOR" in classify_reminder:
        return {"output": "⚠️ This reminder was set by your doctor and cannot be modified. You can only view it."}
    else:
        return {"output": "Sorry, I couldn't process your request."}

    