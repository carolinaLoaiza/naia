import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="🗣️ Voz a texto y texto a voz", layout="centered")

st.title("🎤 Voz a texto y texto a voz (con el navegador)")

st.markdown("Haz clic en el botón para hablar. Se transcribirá y se reproducirá automáticamente.")

components.html("""
    <div>
        <button onclick="startRecognition()" style="font-size:20px;padding:10px 20px;margin-top:10px;">🎙️ Hablar</button>
        <p id="output" style="font-size:18px; margin-top: 20px;"></p>
    </div>

    <script>
        function startRecognition() {
            const output = document.getElementById("output");
            output.innerHTML = "🎧 Escuchando...";

            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                output.innerHTML = "❌ Tu navegador no soporta reconocimiento de voz.";
                return;
            }

            var recognition = new SpeechRecognition();
            recognition.lang = "es-ES";
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.start();

            recognition.onresult = function(event) {
                var transcript = event.results[0][0].transcript;
                output.innerHTML = "📝 <strong>Transcripción:</strong> " + transcript;

                // Texto a voz automático
                var utterance = new SpeechSynthesisUtterance(transcript);
                utterance.lang = "es-ES";
                window.speechSynthesis.speak(utterance);
            };

            recognition.onerror = function(event) {
                output.innerHTML = "❌ Error: " + event.error;
            };

            recognition.onspeechend = function() {
                recognition.stop();
            };
        }
    </script>
""", height=300)
