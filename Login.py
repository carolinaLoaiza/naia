import streamlit as st
import streamlit_authenticator as stauth
import requests

st.set_page_config(
    page_title="NAIA - Login",
    page_icon="assets/Naia window icon.png",
    layout="centered",
    initial_sidebar_state="collapsed"  # o "collapsed"
)

# URL of MockAPI
USERS_API_URL = "https://689c738058a27b18087e39e2.mockapi.io/mock_nhs_api/v1/naia_users"  # reemplaza con tu URL real


# Bring the user from MockAPI
try:
    response = requests.get(USERS_API_URL)
    response.raise_for_status()
    users_data = response.json()
except requests.RequestException as e:
    st.error(f"NHS MockAPI connection error: {e}")
    st.stop()


# Convert users to streamlit_authenticator format
config = {
    "credentials": {
        "usernames": {}
    },
    "cookie": {
        "name": "naia_session",
        "key": "hackathon2025",  
        "expiry_days": 1
    }
}

for user in users_data:
    config["credentials"]["usernames"][user["patient_id"]] = {
        "email": f"{user['patient_id']}@naia.local",  # campo requerido por la librería
        "name": f"Paciente {user['patient_id']}",
        "password": user["passwordHash"]
    }


authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

if "authentication_status" not in st.session_state or st.session_state['authentication_status'] is None:
    st.write("Please enter your :blue[**NHS ID**] as your username.")

try:
    authenticator.login()
except stauth.AuthenticationError as e:
    st.error(e)

# Authenticating user
if st.session_state['authentication_status']: 
    page = st.navigation([
        "pages/Home.py",
        "pages/Chat.py",
        "pages/Symptom Tracker.py",
        "pages/Medications.py",
        "pages/Recovery Check Ups.py",
        "pages/Follow-Up Appointments.py",
        "pages/FAQ.py"])  
    authenticator.logout("Log Out", "sidebar")  
    page.run()
    st.markdown("""
        <style>
            [data-testid=stSidebar] {
                background-color: #ffcfa1;
                /* Opcional: padding, border-radius, etc */
            }
            [data-testid=stSidebarNavItems] * {
                font-family: 'Source Sans', sans-serif, monospace !important;
                color: #ffffff !important;  /* color del texto */
                font-size: 20px !important;
                
            }
        </style>
    """, unsafe_allow_html=True)

elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')

