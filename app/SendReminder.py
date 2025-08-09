from datetime import datetime, timedelta
import re
import threading
import time
from twilio.rest import Client
import streamlit as st

from app.MedicationScheduleManager import MedicationScheduleManager
from app.MedicalRecordManager import MedicalRecordManager

def enviar_sms(destino: str, mensaje: str) -> str:
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
        # Si llega hasta aquí, Twilio aceptó la petición
        print(sms.sid)
        return True
    except Exception as e:
        # Hubo un error creando el mensaje
        print("Error while sending the SMS: {e}")
        return False
    
def get_upcoming_medication(username):
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
        except:
            continue
    return upcoming

# def check_for_reminder_medication (username):
#     upcoming_meds = get_upcoming_medication(username)
#     medicalRecordManager = MedicalRecordManager(username)
#     patientInfo = medicalRecordManager.get_patient_info()
#     phone = patientInfo.get("phone")
    
#     if upcoming_meds:
#         message = "\n".join(upcoming_meds)  # Unir todos los recordatorios en un solo string
#         return enviar_sms(phone, message)    # Aquí llamas a tu función que envía el SMS
#     return False


def monitoring(user):
    username = user
    if "sent_reminders" not in st.session_state:
        st.session_state.sent_reminders = set()
    while True:
        upcoming_meds = get_upcoming_medication(username)
        meds_to_send = [med for med in upcoming_meds if med not in st.session_state.sent_reminders]
        if meds_to_send:
            medicalRecordManager = MedicalRecordManager(username)
            patientInfo = medicalRecordManager.get_patient_info()
            phone = patientInfo.get("phone")
            if phone:
                message = "\n".join(meds_to_send)
                enviado = enviar_sms(phone, message)
                if enviado:
                    # Guardar los mensajes enviados para no repetir
                    for med in meds_to_send:
                        st.session_state.sent_reminders.add(med)

        time.sleep(30)
    
    

def start_monitoring_thread(username):
    if "monitoring" not in st.session_state:
        st.session_state.monitoring = True
        threading.Thread(target=monitoring, args=(username,), daemon=True).start()
        print("While tha app is running. NAIA will send SMS automatically a medication reminder")
