# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# password_plain = "123456"
# hashed_password = pwd_context.hash(password_plain)
# print("HASHED --- " ,hashed_password)
# #  $2b$12$OsiXGsfuL3Fbi8LMbzQliutymm8lBA7/Cv.Qf.etkZqGvGGWTdPgS

import streamlit as st
from pymongo import MongoClient

# Conectar a MongoDB usando secrets
client = MongoClient(st.secrets["MONGO_URI"])

# Seleccionar base de datos y colecciones
db = client["naia_db"]
chat_history_col = db["chat_history"]
symptoms_col = db["symptoms"]
followup_col = db["followupTracker"]
medication_col = db["medicationTracker"]
routine_col = db["routineTracker"]

st.success("Conexión a MongoDB exitosa ✅")

if st.button("Agregar chat de prueba"):
    chat_doc = {
        "patient_id": "111222333",
        "history": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant for post-surgery recovery."
                },
                {
                    "role": "assistant",
                    "content": "Good morning, Mick Jagger. How are you feeling today?\n\nWould you like to report any symptoms or tell me how you're doing?"
                },
                {
                    "role": "user",
                    "content": "Hi Naya, I want to report that I have chest pain. Is something that I have to concern?"
                },
                {
                    "role": "assistant",
                    "content": "📋 Mick Jagger, I'm happy to help with your question. Here's what I can tell you:\n\nAccording to the NHS guidelines, if you have chest pains along with pain and swelling in your leg, it could be a sign of a blood clot in the lungs (pulmonary embolism). This is a serious condition that needs immediate treatment.\n\nPlease call 111 or get help from 111 online. If you're unable to get help online, you can call 999 and ask for an ambulance. Make sure to bring any medicines you take with you.\n\nPlease don't drive to the hospital yourself. Ask someone to drive you or get an ambulance. I'm here to support you, and I want to make sure you get the help you need. Do you have any other concerns or questions?"
                },
                {
                    "role": "user",
                    "content": "I have fever and feel pain in my leg "
                },
                {
                    "role": "assistant",
                    "content": "🔎 The symptom was evaluated as: **moderate**.\n\n🩺:\nMick Jagger, thank you for sharing your symptoms. Here's some guidance:\n\n- Rest and elevate your leg to reduce swelling and ease pain.\n- Continue taking your pain medication, ibuprofen, as directed, and consider taking acetaminophen as needed for fever.\n- Monitor your symptoms closely and seek immediate medical attention if they worsen, you experience difficulty breathing, or you have chest pains.\n\nPlease note that if you experience any of the following, call 111 or seek emergency care:\n- Severe pain or swelling in your leg\n- High fever or chills\n- Oozing or pus from your wound\n- Redness, tenderness, or pain in your knee that's not getting better or is getting worse\n\nIf you have any further questions or concerns, please don't hesitate to ask."
                },
                {
                    "role": "assistant",
                    "content": "Good morning, Mick Jagger. How are you feeling today?\n\nWould you like to report any symptoms or tell me how you're doing?"
                },
                {
                    "role": "user",
                    "content": "Hi Naya, I have feel pain in my leg and febrile"
                },
                {
                    "role": "assistant",
                    "content": "🔎 The symptom was evaluated as: **moderate**.\n\n🩺:\nMick Jagger, thank you for sharing your symptoms. Here's some guidance:\n\n- Please rest and elevate your leg to reduce pain and swelling.\n- Continue to take your prescribed medications, including ibuprofen and acetaminophen, as directed.\n- Monitor your symptoms closely, and if they worsen or you experience difficulty breathing, chest pains, or severe pain, seek emergency care immediately by calling 111 or 999.\n\nPlease note that you should seek immediate medical attention if you experience any of the following:\n- Severe pain or swelling in your leg\n- Difficulty breathing\n- Chest pains\n- Oozing or pus from your wound\n- Redness, tenderness, or swelling in your knee that's not getting better or is getting worse\n\nIf you have any further questions or concerns, please don't hesitate to ask."
                },
                {
                    "role": "assistant",
                    "content": "Good morning, Mick Jagger. How are you feeling today?\n\nWould you like to report any symptoms or tell me how you're doing?"
                },
                {
                    "role": "user",
                    "content": "Hi Naya, I have pain in my chest."
                },
                {
                    "role": "assistant",
                    "content": "🔎 The symptom was evaluated as: **severe**.\n\n🩺:\n🚨 **Potentially urgent symptoms detected.**\nPlease call emergency services or go to the hospital immediately.\nIf you are already in the hospital, inform the medical staff about these symptoms."
                },
                {
                    "role": "assistant",
                    "content": "Good morning, Mick Jagger. How are you feeling today?\n\nWould you like to report any symptoms or tell me how you're doing?"
                },
                {
                    "role": "user",
                    "content": "Could you tell me my allergies ? "
                },
                {
                    "role": "assistant",
                    "content": "💊 **Reminder**:\n- 💊 ibuprofen (400mg) - 00:30\n\n🧘 **Recovery Tasks Due**:\n- 📝 Apply ice to the knee (15 min) a las 00:00\n\n📅 **Appointment Tomorrow**:\n- 📅 Initial post-op assessment after knee replacement at Royal London Hospital - Clinic A, Floor 2 on 2025-08-13 at 18:30\n\nAccording to your medical records, Mick Jagger:\n\nYou have the following allergies:\n- Penicillin\n- Shellfish"
                },
                {
                    "role": "user",
                    "content": "Hi Naya, could you tell me my past medical conditions?"
                },
                {
                    "role": "assistant",
                    "content": "💊 **Reminder**:\n- 💊 ibuprofen (400mg) - 00:30\n\n🧘 **Recovery Tasks Due**:\n- 📝 Apply ice to the knee (15 min) a las 00:00\n\n📅 **Appointment Tomorrow**:\n- 📅 Initial post-op assessment after knee replacement at Royal London Hospital - Clinic A, Floor 2 on 2025-08-13 at 18:30\n\nAccording to your medical records, Mick Jagger:\n\nYou have a past medical history of:\n\n- Appendicitis in 2001\n- Chickenpox in 1965"
                },
                {
                    "role": "assistant",
                    "content": "Good morning, Mick Jagger. How are you feeling today?\n\nWould you like to report any symptoms or tell me how you're doing?"
                },
                {
                    "role": "user",
                    "content": "I just took ibuprophen "
                },
                {
                    "role": "assistant",
                    "content": "✅ Got it! I've marked **ibuprofen** as taken."
                }

        ]
    }
    chat_history_col.insert_one(chat_doc)
    st.write("Historial guardado en MongoDB")

# Consultar historial
if st.button("Mostrar historial"):
    historial = chat_history_col.find_one({"patient_id": "user1"})
    # st.write(historial)
    st.write(historial.get("history", []))



# db = client["mi_base"]
# collection = db["symptoms"]

# # 2. Formulario para guardar datos
# st.title("Reporte de síntomas")
# symptom = st.text_input("Describe tu síntoma")
# if st.button("Guardar"):
#     if symptom:
#         collection.insert_one({"symptom": symptom})
#         st.success("Síntoma guardado en MongoDB")
#     else:
#         st.warning("Escribe un síntoma antes de guardar")

# # 3. Mostrar datos guardados
# st.subheader("Síntomas registrados:")
# for doc in collection.find():
#     st.write(f"- {doc['symptom']}")
