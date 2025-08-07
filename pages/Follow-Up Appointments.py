import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from app.AppointmentManager import AppointmentManager



# def status_with_tristate(flag, date_str):
#     date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
#     if flag is True:
#         return "✅ Yes"
#     elif date_obj < today:
#         return "❌ No"
#     else:
#         return "⏳"
    

if not st.session_state.get("authentication_status"):
    st.warning("Please log in first.")
    st.stop()

USER_ID = st.session_state["username"]
# history_file = f"data/history_{USER_ID}.json"
# appointment_tracker_file = f"data/followupTracker_{USER_ID}.json"
appointmentManager = AppointmentManager(USER_ID)
appointments = appointmentManager.return_appointment_info()

# def create_tracker_if_needed():
#     manager = AppointmentManager()
#     if not os.path.exists(appointment_tracker_file):
#         return manager.create_followup_tracker_from_history(history_file, appointment_tracker_file)
#     else:
#         return manager.load(appointment_tracker_file)

# appointments = return_appointment_info()

# Configurar página
if "page_config_set" not in st.session_state:
    st.set_page_config(
        page_title="NAIA - Follow-ups",
        page_icon="assets/Naia window icon.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state.page_config_set = True

st.title(":orange[NAIA - Follow-up Appointments]")
st.subheader("All scheduled post-surgical medical check-ups")


if not appointments:
    st.info("No follow-up appointments found.")
    st.stop()

# Mostrar tabla completa (sin edición)
df = pd.DataFrame(appointments)
df["attended_status"] = df.apply(lambda row: appointmentManager.status_with_tristate(row["attended"], row["date"]), axis=1)
df["reminder_status"] = df.apply(lambda row: appointmentManager.status_with_tristate(row["reminder_sent"], row["date"]), axis=1)

display_df = df[[
    "date", "time", "department", "location", "clinician", "reason",
     "reminder_status", "attended_status", "notes"
]].rename(columns={
    "reminder_status": "Reminder Sent",
    "attended_status": "Attended",
    "clinician": "Clinician",
    "location": "Location",
    "reason": "Reason",
    "department": "Department",
    "date": "Date",
    "time": "Time",
    "confirmed": "Confirmed",
    "notes": "Notes"
})

# Renderizar con AgGrid (solo lectura)
gb = GridOptionsBuilder.from_dataframe(display_df)
gb.configure_pagination()
gb.configure_default_column(editable=False, sortable=True, filter=True, resizable=True, autoWidth=True)
grid_options = gb.build()

AgGrid(
    display_df,
    gridOptions=grid_options,
    update_mode="NO_UPDATE",
    theme="balham",
    height=500,
    # allow_unsafe_jscode=True
    use_container_width=True 
)
