from datetime import datetime, timedelta
import re
import threading
import time
from twilio.rest import Client
import streamlit as st

from app.MedicationScheduleManager import MedicationScheduleManager
from app.MedicalRecordManager import MedicalRecordManager
from app.AppointmentManager import AppointmentManager

def send_sms(destino: str, mensaje: str) -> str:
    """
    Sends an SMS using Twilio.

    Args:
        destino (str): Phone number in international format (+1234567890).
        mensaje (str): Content of the SMS to send.

    Returns:
        bool: True if the SMS was sent successfully, False if there was an error or invalid number.
    """
    account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
    auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
    twilio_number = st.secrets["TWILIO_PHONE_NUMBER"]

    if not destino or not re.match(r'^\+\d{10,15}$', destino):
        return False
    client = Client(account_sid, auth_token)
    try:
        sms = client.messages.create(
            body=mensaje,
            from_=twilio_number,
            to=destino
        )
        # print(sms.sid)
        return True
    except Exception as e:
        print("Error while sending the SMS: {e}")
        return False
    
def get_upcoming_medication(username):
    """
    Gets the list of medications that need to be taken within ±1 minute.

    Args:
        username (str): Username to identify the medication tracker.

    Returns:
        list: Reminder messages for medications that are due soon.
    """
    now = datetime.now()
    start = now - timedelta(minutes=1)
    end = now + timedelta(minutes=1)
    medicationScheduleManager = MedicationScheduleManager(username)
    tracker = medicationScheduleManager.load_tracker()
    upcoming = []
    for med in tracker:
        if med.get("taken"):
            continue
        dt_str = f"{med['date']} {med['time']}"
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            if start <= dt <= end:
                upcoming.append(f"It is time to take {med['med_name']} - ({med['dose']})")
        except Exception as e:
            print(f"Error parsing med datetime: {e}")
            continue
    return upcoming

def get_upcoming_appointments(username):
    """
    Gets upcoming medical appointments within the next 24 hours.

    Args:
        username (str): Username to identify the appointment tracker.

    Returns:
        list: Reminder messages for upcoming appointments.
    """
    now = datetime.now()
    start = now
    end = now + timedelta(hours=24)
    appointmentManager = AppointmentManager(username)
    tracker = appointmentManager.load_appointment_tracker()
    upcoming = []
    for appointment in tracker:
        if appointment.get("reminder_sent"):
            continue
        dt_str = f"{appointment['date']} {appointment['time']}"
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            if start <= dt <= end:
                upcoming.append(
                    f"Reminder: {appointment['department']} at {appointment['location']} "
                    f"with {appointment['clinician']} on {appointment['date']} at {dt.strftime('%H:%M')}"
                )
                appointmentManager.mark_reminder_as_sent(appointment['date'], appointment['time'])
        except Exception as e:
            print(f"Error parsing appointment datetime: {e}")
            continue
    return upcoming

def monitoring(user):
    """
    Continuous monitoring loop that sends reminders for medications and appointments.

    Args:
        user (str): Username for which reminders should be sent.

    Notes:
        - Avoids sending duplicate reminders using st.session_state.sent_reminders.
        - Runs indefinitely, checking every 30 seconds.
    """
    username = user
    if "sent_reminders" not in st.session_state:
        st.session_state.sent_reminders = set()
    while True:
        upcoming_meds = get_upcoming_medication(username)
        if upcoming_meds: 
            meds_to_send = [med for med in upcoming_meds if med not in st.session_state.sent_reminders]
            if meds_to_send:
                medicalRecordManager = MedicalRecordManager(username)
                patientInfo = medicalRecordManager.get_patient_info()
                phone = patientInfo.get("phone")
                if phone:
                    message = "\n".join(meds_to_send)                    
                    if send_sms(phone, message):
                        # Save the sent messages to avoid repetition
                        for med in meds_to_send:
                            st.session_state.sent_reminders.add(med)
        # Appointment reminders
        upcoming_appts = get_upcoming_appointments(username)
        appts_to_send = [appt for appt in upcoming_appts if appt not in st.session_state.sent_reminders]
        if appts_to_send:
            medicalRecordManager = MedicalRecordManager(username)
            patientInfo = medicalRecordManager.get_patient_info()
            phone = patientInfo.get("phone")
            if phone:
                message = "\n".join(appts_to_send)
                if send_sms(phone, message):
                    for appt in appts_to_send:
                        st.session_state.sent_reminders.add(appt)
        
        time.sleep(30)
    
    

def start_monitoring_thread(username):
    """
    Starts the background monitoring thread if it does not already exist.

    Args:
        username (str): Username for starting the reminder monitoring.

    Notes:
        - Ensures that only one monitoring thread runs per session.
        - The thread continuously runs the monitoring() function.
    """
    if "monitoring" not in st.session_state:
        st.session_state.monitoring = True
        threading.Thread(target=monitoring, args=(username,), daemon=True).start()
        # print("While tha app is running. NAIA will send SMS automatically a medication reminder")
