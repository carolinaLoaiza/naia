import base64
import datetime
import random
import streamlit as st
from streamlit_chat_widget import chat_input_widget
from openai import OpenAI
from streamlit_extras.bottom_container import bottom 
import os
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import streamlit.components.v1 as components

from app.GroqChat import GroqChat
from app.ChatHistoryManager import ChatHistoryManager
from app.MedicalRecordManager import MedicalRecordManager
from graph.LangGraph import build_graph


def play_audio(text: str, filename: str = "voice.mp3", voice: str = "shimmer"):
    try:
        tts_response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        tts_response.write_to_file(filename)
        with open(filename, "rb") as f:
            audio_bytes = f.read()
            b64 = base64.b64encode(audio_bytes).decode()
            rand_id = random.randint(0, 999999)
            components.html(f"""
                <html>
                <body>
                    <audio id="audio{rand_id}" autoplay>
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                    <script>
                        const audio = document.getElementById("audio{rand_id}");
                        setTimeout(() => {{
                            audio.play().catch(e => console.log("Playback error:", e));
                        }}, 500);  // medio segundo de retraso para evitar corte
                    </script>
                </body>
                </html>
            """, height=0)
    except Exception as e:
        st.warning(f"Could not convert text to speech: {e}")


# Autenticathion
if not st.session_state.get("authentication_status"):
    st.warning("Please log in first.")
    st.stop()

username = st.session_state["username"]


#LLMs API Keys
openai_api_key = st.secrets.get("OPENAI_API_KEY")
groq_api_key = st.secrets.get("GROQ_API_KEY")
if not groq_api_key:
    st.error("Groq API key not found.")
    st.stop()
if not openai_api_key:
    st.error("OpenAI API key was not found.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# Setup Chat page
if "page_config_set" not in st.session_state:
    st.set_page_config(
        page_title="NAIA assistant",
        page_icon="assets/nurse.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state.page_config_set = True
    st.sidebar.title("Opciones")

st.title(":orange[NAIA]")
st.subheader("Your post-surgery assistant")

#Initialize variables
groqChat = GroqChat()
chatHistoryManager = ChatHistoryManager(user_id=username)  # Use a default user ID for simplicity
# Estado del chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = chatHistoryManager.load()

medical_record_manager = MedicalRecordManager(username)
if not medical_record_manager.record:
    #st.warning("No medical history was found for your account. You can still chat with NAIA, but some personalized suggestions may be limited.")
    #patient_name = username
    st.error(
            f"⚠️ No medical record found for user **{username}**.\n\n"
            "NAIA needs your medical data to provide safe and accurate guidance. "
            "Please contact support to upload your medical history to continue."
        )
    st.stop()
else:
    patient_name = medical_record_manager.record.get("name", "Patient")


if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = True
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    welcome_message = (
        f"{greeting}, {patient_name}. How are you feeling today?\n\n"
        "Would you like to report any symptoms or tell me how you're doing?"
    )
    st.session_state.chat_history.append(AIMessage(content=welcome_message))
    play_audio(welcome_message, filename="welcome_audio.mp3")

if "agent_graph" not in st.session_state:
    st.session_state.agent_graph = build_graph()


# Container for the chat history
chat_box = st.container()
# Include chat input
with bottom():
    response = chat_input_widget()

if response:
    user_text = None
    is_voice_input = False
    # TEXT
    if "text" in response:
        user_text = response["text"]
        st.session_state.chat_history.append(HumanMessage(content=user_text))
    # AUDIO
    elif "audioFile" in response:
        try:
            audio_bytes = bytes(response["audioFile"])
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_bytes)
            with open("temp_audio.wav", "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    language="en"
                )
            if transcript and hasattr(transcript, "text"):
                user_text = transcript.text
                is_voice_input = True  
                st.session_state.chat_history.append(HumanMessage(content=user_text))
            else:
                st.warning("It cannot be transcripted the audio.")
        except Exception as e:
            st.error(f"Transcription error: {e}")
    # Get response if the input is a valid text from the user
    if user_text:
        # Build a LLM history
        messages = groqChat.get_initial_messages()
        for msg in st.session_state.chat_history:
            if isinstance(msg, HumanMessage):
                messages.append(groqChat.human_message(msg.content))
            elif isinstance(msg, AIMessage):
                messages.append(groqChat.ai_message(msg.content))

        #assistant_reply = groqChat.get_response(messages)
        agent_state = {"input": user_text, "output": ""}
        final_state = st.session_state.agent_graph.invoke(agent_state)
        assistant_reply = final_state["output"]

        st.session_state.chat_history.append(AIMessage(content=assistant_reply))
        chatHistoryManager.save(st.session_state.chat_history)

        # Speak response if the input was voice 
        if is_voice_input:
            play_audio(assistant_reply, filename="assistant_reply.mp3")

# Show chat history after processing the input
with chat_box:
    for msg in st.session_state.chat_history:
        if isinstance(msg, SystemMessage):
            continue
        role = "user" if msg.type == "human" else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)    

st.markdown("""
    <style>
    iframe[title="streamlit_chat_widget.chat_input_widget"] {
        height: 120px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <script>
    window.scrollTo(0, document.body.scrollHeight);
    </script>
""", unsafe_allow_html=True)
