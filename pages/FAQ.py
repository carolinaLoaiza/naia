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
with st.expander("What is this chatbot for?"):
    st.markdown("This chatbot is designed to support you during your post-surgery recovery. It offers helpful reminders, tracks your symptoms, answers your questions, and gives guidance tailored to your specific surgery and health condition.")

with st.expander("Can this chatbot replace my doctor?"):
    st.markdown("No, it cannot. The chatbot is here to complement your recovery process, not replace medical advice. Always consult your doctor for urgent or serious health concerns.")

with st.expander("What surgeries does this chatbot support?"):
    st.markdown("""The chatbot currently supports recovery guidance for:
            - Cataract surgery
            - Hip/knee replacement
            - Gallbladder removal
            - Hernia repair
            - Appendectomy
            ...with more surgeries being added soon.""")


st.markdown("#### Accessibility & Voice Interaction")

with st.expander("I have blurry vision after surgery. How can I use the chatbot?"):
    st.markdown("You can interact with the chatbot using voice commands. Just enable voice chat when the app starts, and it will guide you step by step without needing to read or type.")

with st.expander("Can I use this chatbot if I’m not very tech-savvy?"):
    st.markdown("Absolutely! The chatbot is designed with simple buttons, voice options, and friendly responses. No technical knowledge is required.")

st.markdown("#### Health Monitoring Features")

with st.expander("Can I report how I feel to the chatbot?"):
    st.markdown("Yes, you can tell the chatbot your symptoms (like pain, nausea, dizziness), and it will offer appropriate suggestions—or alert you if it thinks you should contact your doctor.")

with st.expander("Does it remind me when to take my medications?"):
    st.markdown("Yes! Once you input your medication schedule, the chatbot can send reminders to take your meds and even check if you’ve done so.")

with st.expander("Can the chatbot check if my symptoms are normal?"):
    st.markdown("Yes. Based on your surgery type and health status, the chatbot can help you identify normal vs. concerning symptoms and advise you on the next steps.")

st.markdown("#### Privacy & Safety")

with st.expander("Is my health information safe?"):
    st.markdown("Yes, we follow strict data protection rules. Your health details are confidential, secure, and never shared without your consent.")

with st.expander("Can someone else use the chatbot on my behalf?"):
    st.markdown("Yes. A trusted caregiver or family member can use the chatbot with your permission to help track your recovery.")


st.markdown("#### Additional Features & Help")

with st.expander("Can I use the chatbot if I had multiple surgeries?"):
    st.markdown("Yes, just select or mention all your relevant procedures, and the chatbot will adapt its guidance accordingly.")

with st.expander("What if I don’t know what’s wrong but I feel off?"):
    st.markdown("The chatbot can help you log how you're feeling and check for common post-surgery concerns. If anything is outside normal recovery, it will recommend next steps.")

with st.expander("Can I talk to a real person through the chatbot?"):
    st.markdown("While the chatbot handles routine questions, there’s also an escalation feature where you can request help from a real health support team if available.")

with st.expander("How often should I use the chatbot?"):
    st.markdown("We recommend checking in at least once a day or whenever you experience symptoms or need help remembering something.")
    

# st.markdown("#### Privacy, Platform Guidelines, and Intellectual Property")

# with st.expander("Is my information kept confidential on GPT Lab?"):
#     st.markdown("Yes, we take your privacy and confidentiality very seriously. We do not store any personally identifiable information, and instead use a secure hashing algorithm to store a hashed version of your OpenAI API Key. Additionally, session transcripts are encrypted.")

# with st.expander("How does NAIA ensure the security of my information?"):
#     st.markdown("""We use the SHA-256 PBKDF2 algorithm, a highly secure one-way hashing algorithm, to hash your OpenAI API Key and store it securely. This ensures that your key is protected and cannot be used for any unauthorized purposes.     
#                     Additionally, we use a symmetric AES-128 encryption algorithm, with a unique key for each user, to encrypt your chat transcripts with the AI Assistants.""")

# with st.expander("Are there any restrictions on the type of NAIA as an AI Assistants?"):
#     st.markdown("""
#     Our Terms of Use have outlined some common sense restrictions you should follow. Please review our Terms of Use, available on the Terms page, for more information. 
#     Additionally, since our NAIA Assistant use the Groq AI language models, you should also comply with the [Groq Cloud Usage policies](https://groq.com/terms-of-use).  \n
#     We recommend ...  \n
#     Please note that NAIA does not assume ....
#     """)
# with st.expander("Who owns the prompts created in NAIA?"):
#     st.markdown("You do! The prompts created by the users in NAIA belong to the users themselves. NAIA is a platform that enables users to interact with AI Assistants powered by Groq language models, and the prompts created by the users in the app are the property of the users themselves. NAIA does not claim any ownership or rights to the prompts created by the users.")

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
