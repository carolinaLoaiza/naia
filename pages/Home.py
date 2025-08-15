import streamlit as st 
from PIL import Image

from app import SendReminder
from app.MedicalRecordManager import MedicalRecordManager


if "page_config_set" not in st.session_state:
    st.set_page_config(
        page_title="NAIA assistant",
        page_icon="assets/Naia window icon.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state.page_config_set = True


# Autenticathion
if not st.session_state.get("authentication_status"):
    st.warning("Please log in first.")
    st.stop()

username = st.session_state["username"]
medicalRecordManager = MedicalRecordManager(username)
if not medicalRecordManager.record:
    st.error(f"⚠️ No medical record found for user **{username}**.\n\n")
    st.info("NAIA needs your medical data to provide safe and accurate guidance. Please contact support to upload your medical history to continue.")
    st.stop()
else:
    patient_name = medicalRecordManager.record.get("name", "Patient")
st.title(":orange[Welcome to NAIA {patient_name}]".format(patient_name=patient_name))

st.markdown("""
Nurse Artificial Intelligence Assistant - NAIA is your smart post-surgery assistant.  
Track your symptoms, medications, and communicate easily during your recovery process.  
""")

st.divider()

# ---- Section: Navigation Cards ----

# Optional icons/images
icons = {
    "Chat": "assets/Naia icon v2.jpeg",  # Or use "images/chat_icon.png"
    "Symptom Tracker": "assets/Symptom icon v2.jpeg",
    "Medications": "assets/Medication icon v2.jpeg",
    "Routine": "assets/Recovery routine icon v7.png",
    "Appointment": "assets/Appointment icon v6.png",
    "FAQ": "assets/Faq icon v2.jpeg"
}



medicalRecordManager = MedicalRecordManager(username)
patientInfo = medicalRecordManager.get_patient_info()
phone = patientInfo.get("phone")
if not phone:
    if not st.session_state.get("no_phone_toast_shown"):
        st.toast("No phone number is linked to the client for receiving reminders. Please visit the NHS portal and update your details.", icon="❗")
        st.session_state.no_phone_toast_shown = True    
else:
    SendReminder.start_monitoring_thread(username)



# Función para renderizar cada acceso
def render_access(title, description, icon_path, page_url=None):
    st.image(icon_path, width=200)
    st.markdown(f"### {title}")
    st.markdown(f" {description}.")    
    if st.button(f"Go to {title}", key=title):
        st.switch_page(page_url) if page_url else st.info("Page not available")

# ---- Diseño en 2x2 ----
col1, col2, col3 = st.columns(3)
with col1:
    render_access("Chat", "Talk to NAIA for guidance, questions, and post-op support", icons["Chat"], "pages/Chat.py")
with col2:
    render_access("Symptom Tracker", "Log your daily symptoms and get real-time insights", icons["Symptom Tracker"], "pages/Symptom Tracker.py")
with col3:
    render_access("Medications", "View your current prescriptions and track usage", icons["Medications"], "pages/Medications.py")

col4, col5, col6 = st.columns(3)
with col4:
    render_access("Recovery Check-Ups", "Daily tasks and care reminders to support your healing after surgery", icons["Routine"], "pages/Recovery Check Ups.py")
with col5:
    render_access("Follow-Up Appointments", "Keep track of your upcoming medical visits and check-ins", icons["Appointment"], "pages/Follow-Up Appointments.py")
with col6:
    render_access("FAQ", "Find quick answers to common questions about navigating features, managing your recovery tasks, tracking appointments, and customizing your settings.", icons["FAQ"], "pages/FAQ.py")

# Footer or credits
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; font-size: 0.9em; color: gray; padding-top: 10px;'>
        Built with caffeine, curiosity, and questionable Wi-Fi. <br>
        <strong>Disclaimer/Important:</strong> NAIA is an academic prototype and should not be used as a replacement for your GP. <br>
        <em>Northumbria University London - NUL </em> – Contemporary Computing and Digital Technologies module
    </div>
    """,
    unsafe_allow_html=True
)
