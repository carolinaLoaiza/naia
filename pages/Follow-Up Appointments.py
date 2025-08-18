import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from app.AppointmentManager import AppointmentManager

if not st.session_state.get("authentication_status"):
    st.warning("Please log in first.")
    st.stop()

USER_ID = st.session_state["username"]
appointmentManager = AppointmentManager(USER_ID)
appointments = appointmentManager.return_appointment_info()


# Set up page
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

# Show complete table (read-only)
df = pd.DataFrame(appointments)
# df["attended_status"] = df.apply(lambda row: appointmentManager.status_with_tristate(row["attended"], row["date"]), axis=1)
df["reminder_status"] = df.apply(lambda row: appointmentManager.status_with_tristate(row["reminder_sent"], row["date"]), axis=1)

display_df = df[[
    "date", "time", "department", "location", "clinician", "reason",
     "reminder_status"
    #  , "attended_status"
    , "notes"
]].rename(columns={
    "reminder_status": "Reminder Sent",
    # "attended_status": "Attended",
    "clinician": "Clinician",
    "location": "Location",
    "reason": "Reason",
    "department": "Department",
    "date": "Date",
    "time": "Time",
    "confirmed": "Confirmed",
    "notes": "Notes"
})

# Render with AgGrid (read-only)
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
