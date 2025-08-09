import streamlit as st 

if "page_config_set" not in st.session_state:
    st.set_page_config(
        page_title="NAIA assistant",
        page_icon="assets/Naia window icon.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state.page_config_set = True
st.title(":orange[NAIA - FAQ ]")

# Autenticathion
if not st.session_state.get("authentication_status"):
    st.warning("Please log in first.")
    st.stop()

username = st.session_state["username"]

st.markdown(
    "<style>#MainMenu{visibility:hidden;}</style>",
    unsafe_allow_html=True
)


#au.render_cta()

#st.title("FAQ")

#st.markdown("---")
#au.robo_avatar_component()

st.markdown("#### General")
with st.expander("What is NAIA?", expanded=False):
    st.markdown("NAIA is a real-time AI assistant designed to support post-operative patients through natural, conversational	communication. Using medically reviewed content and hospital-approved protocols, NAIA provides accurate, 24/7 guidance to patients recovering from surgery, reducing uncertainty, preventing complications, and relieving nursing staff of repetitive questions. For nurses, NAIA acts as a virtual partner, easing workload pressures and improving time management. For hospitals, it means better patient experience, fewer readmissions, and more scalable care. In a system facing rising demand and limited staffing, NAIA offers a smart, sustainable solution to extend high-quality post-op care without increasing workforce strain.")


with st.expander("Why use NAIA?"):
    st.markdown("NAIA aims to ....")

with st.expander("QUESTION 3?"):
    st.markdown("ANSWER 3....")

with st.expander("QUESTION 4?"):
    st.markdown("ANSWER 4....")

st.markdown("#### How to use NAIA")

with st.expander("QUESTION 1?"):
    st.markdown("ANSWER 1....")

with st.expander("QUESTION 2?"):
    st.markdown("ANSWER 2....")

with st.expander("QUESTION 3?"):
    st.markdown("ANSWER 3....")

with st.expander("QUESTION 4?"):
    st.markdown("ANSWER 4....")

with st.expander("QUESTION 5?"):
    st.markdown("ANSWER 5....")

with st.expander("QUESTION 6?"):
    st.markdown("ANSWER 6....")

st.markdown("#### Privacy, Platform Guidelines, and Intellectual Property")

with st.expander("Is my information kept confidential on GPT Lab?"):
    st.markdown("Yes, we take your privacy and confidentiality very seriously. We do not store any personally identifiable information, and instead use a secure hashing algorithm to store a hashed version of your OpenAI API Key. Additionally, session transcripts are encrypted.")

with st.expander("How does NAIA ensure the security of my information?"):
    st.markdown("""We use the SHA-256 PBKDF2 algorithm, a highly secure one-way hashing algorithm, to hash your OpenAI API Key and store it securely. This ensures that your key is protected and cannot be used for any unauthorized purposes. 
    
Additionally, we use a symmetric AES-128 encryption algorithm, with a unique key for each user, to encrypt your chat transcripts with the AI Assistants.""")

with st.expander("Are there any restrictions on the type of NAIA as an AI Assistants?"):
    st.markdown("""
    Our Terms of Use have outlined some common sense restrictions you should follow. Please review our Terms of Use, available on the Terms page, for more information. 
    Additionally, since our NAIA Assistant use the Groq AI language models, you should also comply with the [Groq Cloud Usage policies](https://groq.com/terms-of-use).  \n
    We recommend ...  \n
    Please note that NAIA does not assume ....
    """)
with st.expander("Who owns the prompts created in NAIA?"):
    st.markdown("You do! The prompts created by the users in NAIA belong to the users themselves. NAIA is a platform that enables users to interact with AI Assistants powered by Groq language models, and the prompts created by the users in the app are the property of the users themselves. NAIA does not claim any ownership or rights to the prompts created by the users.")