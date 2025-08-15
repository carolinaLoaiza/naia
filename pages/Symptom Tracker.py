import streamlit as st 
import os
import json
import pandas as pd
from datetime import datetime
from app.SymptomManager import SymptomManager

if "page_config_set" not in st.session_state:
    st.set_page_config(
        page_title="NAIA assistant",
        page_icon="assets/Naia window icon.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state.page_config_set = True
st.title(":orange[NAIA - My Symptoms]")
st.subheader("Here's a summary of your reported symptoms")


# Autenticathion
if not st.session_state.get("authentication_status"):
    st.warning("Please log in first.")
    st.stop()

username = st.session_state["username"]
symptom_manager = SymptomManager(user_id=username)

symptoms = symptom_manager.get_all()

if not symptoms:
    st.info("You haven’t reported any symptoms yet.")
    st.stop()


# Mostrar los síntomas en tarjetas simples
for entry in reversed(symptoms[-10:]):  # últimos 10
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            symptom_list = entry.get("symptoms", [])
            symptom_names = [s.get("name", "unknown") for s in symptom_list]
            # locations = [s.get("location", "unknown") for s in symptom_list]
            locations = [s["location"] if s.get("location") else "unknown" for s in symptom_list]
            # durations = [f"{s.get('duration_days', '?')}d" for s in symptom_list]
            durations = [f"{s.get('duration_days') or '?'}d" for s in symptom_list]
            severities = [s.get("severity", "unknown") or "unknown" for s in symptom_list]

            st.markdown(f"**📝 Symptoms:** {', '.join(symptom_names)}")
            st.markdown(f"**📍 Locations:** {', '.join(locations)}")
            st.markdown(f"**📆 Date:** {entry.get('timestamp', 'N/A')[:10]}")
            st.markdown(f"**⏳ Durations:** {', '.join(durations)}")
            st.markdown(f"**⚠️ Severity:** `{entry.get('overall_severity', 'unknown')}`")
        with col2:
            # Usa alguna lógica si quieres marcar atención
            if entry.get("overall_severity") in ["severe", "high"]:
                st.error("🚨 Requires Attention")
            else:
                st.success("✅ Stable")
        st.markdown("---")

# Convertir a DataFrame para vista expandida
df = pd.DataFrame(symptoms)
# Mostrar los síntomas en tarjetas simples
# for entry in reversed(symptoms[-10:]):  # Solo los últimos 10 para no saturar
#     with st.container():
#         col1, col2 = st.columns([3, 1])
#         with col1:
#             st.markdown(f"**📝 Symptoms:** {', '.join(entry.get('symptoms', []))}")
#             st.markdown(f"**📍 Location:** {entry.get('location', 'Not specified')}")
#             st.markdown(f"**📆 Date:** {entry.get('timestamp', 'N/A')[:10]}")
#             st.markdown(f"**⏳ Duration:** {entry.get('duration', 'N/A')}")
#             st.markdown(f"**⚠️ Severity:** `{entry.get('severity', 'unknown')}`")
#         with col2:
#             if entry.get("requires_attention"):
#                 st.error("🚨 Requires Attention")
#             else:
#                 st.success("✅ Stable")
#         st.markdown("---")
# # Convertir lista a DataFrame
# df = pd.DataFrame(symptoms)

# Asegurar campo 'mensaje_original' existe
if "input_text" not in df.columns:
    df["input_text"] = "N/A"

# Expansor con mensajes originales
with st.expander("🗣️ View original messages"):
    for entry in df.itertuples():
        st.markdown(f"**🕒 {entry.timestamp[:19]}**")
        st.markdown(f"**💬 Original Message:** {entry.input_text}")
        st.divider()
        

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
