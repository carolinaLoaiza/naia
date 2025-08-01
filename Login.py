import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(
    page_title="NAIA - Login",
    page_icon="assets/nurse.png",
    layout="centered",
    initial_sidebar_state="collapsed"  # o "collapsed"
)


with open('auth_config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)
try:
    authenticator.login()
except stauth.AuthenticationError as e:
    st.error(e)


# Authenticating user
if st.session_state['authentication_status']: 
    page = st.navigation([
        "pages/Home.py",
        "pages/Chat.py",
        "pages/Symptoms.py",
        "pages/Medication.py",
        "pages/FAQPage.py"])  # Parámetro nombrado
    authenticator.logout("Log Out", "sidebar")  # Al final
    page.run()
    st.markdown("""
        <style>
            [data-testid=stSidebar] {
                background-color: #ffa568;
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
