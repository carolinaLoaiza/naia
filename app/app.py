import base64
import random
import uuid
import streamlit as st
from streamlit_chat_widget import chat_input_widget
from openai import OpenAI
from streamlit_extras.bottom_container import bottom 
import os
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import streamlit.components.v1 as components

from GroqChat import GroqChat
from ChatHistoryManager import ChatHistoryManager

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
st.set_page_config(
    page_title="NAIA assistant",
    page_icon="assets/nurse.png",
    layout="centered",
    initial_sidebar_state="expanded"  # o "collapsed"
)
st.title(":orange[NAIA]")
st.subheader("Your post-surgery assistant")

#Initialize variables
groqChat = GroqChat()
chatHistoryManager = ChatHistoryManager(user_id="user1")  # Use a default user ID for simplicity

# Estado del chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = chatHistoryManager.load()
    #[        "Hello! I am your Doctor AI Assistant. How can I help you?"]


# Container for the chat history
chat_box = st.container()
# Include chat input
with bottom():
    response = chat_input_widget()



if response:
    user_text = None
    is_voice_input = False

    # 1. TEXTO
    if "text" in response:
        user_text = response["text"]
        #st.session_state.chat_history.append(f"You: {user_text}")
        st.session_state.chat_history.append(HumanMessage(content=user_text))
    # 2. AUDIO
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
                is_voice_input = True  # Solo usamos TTS si vino de voz
                #st.session_state.chat_history.append(f"You (voice): {user_text}")
                st.session_state.chat_history.append(HumanMessage(content=user_text))

            else:
                st.warning("No se pudo transcribir el audio.")
        except Exception as e:
            st.error(f"Error al transcribir: {e}")

    # 3. Obtener respuesta si tenemos texto válido
    if user_text:
        # Construir historial para LLM
        messages = groqChat.get_initial_messages()
        for msg in st.session_state.chat_history:
        #    if msg.startswith("You") or msg.startswith("You (voice)"):
        #        messages.append(groqChat.human_message(msg.split(":", 1)[1].strip()))
        #    elif msg.startswith("AI:"):
        #        messages.append(groqChat.ai_message(msg.split(":", 1)[1].strip()))
            if isinstance(msg, HumanMessage):
                messages.append(groqChat.human_message(msg.content))
            elif isinstance(msg, AIMessage):
                messages.append(groqChat.ai_message(msg.content))

        assistant_reply = groqChat.get_response(messages)
        #st.session_state.chat_history.append(f"AI: {assistant_reply}")
        st.session_state.chat_history.append(AIMessage(content=assistant_reply))
        chatHistoryManager.save(st.session_state.chat_history)

        # 4. Si el input fue por voz → también responder con voz
        if is_voice_input:
            try:
                tts_response = client.audio.speech.create(
                    model="tts-1",
                    voice="shimmer",
                    input=assistant_reply
                )
                tts_response.write_to_file("assistant_reply.mp3")
                with open("assistant_reply.mp3", "rb") as f:
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
                                audio.play().catch(e => console.log("Playback error:", e));
                            </script>
                        </body>
                        </html>
                    """, height=0)

                    
            except Exception as e:
                st.warning(f"The response could not be converted to voice: {e}")
 



# Mostrar historial *después* de procesar input
with chat_box:
    #for message in st.session_state.chat_history:
    #    st.write(message)
    for msg in st.session_state.chat_history:
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