import base64
import os
import streamlit as st
from streamlit_chat_widget import chat_input_widget
from openai import OpenAI
from streamlit_float import float_init


#load_dotenv()
float_init()
footer_container = st.container()


openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
if not openai_api_key:
    st.error("⚠️ OpenAI API key no encontrada. Defínela en st.secrets o como variable de entorno.")
    st.stop()
    
client = OpenAI(api_key=openai_api_key)


# Estado del chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        "Hello! I am your Doctor AI Assistant. How can I help you?"
    ]

# Contenedor para el historial
chat_box = st.container()

# Procesar input
response = chat_input_widget()

if response:
    if "text" in response:
        user_text = response["text"]
        st.session_state.chat_history.append(f"You: {user_text}")

    elif "audioFile" in response:
        try:
            audio_bytes = bytes(response["audioFile"])
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_bytes)

            with open("temp_audio.wav", "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1"
                )

            if transcript and hasattr(transcript, "text"):
                user_text = transcript.text
                st.session_state.chat_history.append(f"You (voice): {user_text}")

                # Simular respuesta
                assistant_reply = "Claro, entiendo tu pregunta."
                st.session_state.chat_history.append(f"AI: {assistant_reply}")

                # Generar voz para la respuesta
                tts_response = client.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input=assistant_reply
                )
                tts_response.write_to_file("assistant_reply.mp3")

                # Leer y reproducir sin mostrar reproductor
                with open("assistant_reply.mp3", "rb") as f:
                    audio_bytes = f.read()
                    b64 = base64.b64encode(audio_bytes).decode()
                    st.markdown(f"""
                    <audio autoplay>
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No se pudo transcribir el audio.")
        except Exception as e:
            st.error(f"Error al transcribir: {e}")

# Mostrar historial *después* de procesar input
with chat_box:
    for message in st.session_state.chat_history:
        st.write(message)