import streamlit as st 
from PIL import Image


if "page_config_set" not in st.session_state:
    st.set_page_config(
        page_title="NAIA assistant",
        page_icon="assets/nurse.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state.page_config_set = True
st.title(":orange[Welcome to NAIA]")

st.markdown("""
Nurse Artificial Intelligence Assistant - NAIA is your smart post-surgery assistant.  
Track your symptoms, medications, and communicate easily during your recovery process.  
""")

st.divider()

# ---- Section: Navigation Cards ----

# Optional icons/images
icons = {
    "Chat": "assets/Naia v2 icon.png",  # Or use "images/chat_icon.png"
    "Symptom Tracker": "assets/sympton icon.png",
    "Medications": "assets/medication icon.png",
    "Routine": "assets/routine icon.png",
    "FAQ": "assets/faq icon.png"
}


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
    render_access("Symptom Tracker", "Log your daily symptoms and get real-time insights", icons["Symptom Tracker"], "pages/Symptoms.py")
with col3:
    render_access("Medications", "View your current prescriptions and track usage", icons["Medications"], "pages/Medication.py")

col4, col5, col6 = st.columns(3)
with col4:
    render_access("Routine", "View your current post surgery recommendations and track usage", icons["Routine"], "pages/Routine.py")
with col5:
    render_access("FAQ", "Find answers to the most common recovery questions", icons["FAQ"], "pages/FAQ.py")

# Footer or credits
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; font-size: 0.9em; color: gray; padding-top: 10px;'>
        Built with caffeine, curiosity, and questionable Wi-Fi. <br>
        <strong>NAIA</strong> is an academic prototype – not quite your GP (yet). <br>
        <em>Northumbria University London - NUL </em> – Contemporary Computing and Digital Technologies module
    </div>
    """,
    unsafe_allow_html=True
)
