from zoneinfo import ZoneInfo
import streamlit as st
import json
import os
from datetime import datetime, timedelta, time
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from app.MedicationScheduleManager import MedicationScheduleManager

#Autenticathion
if not st.session_state.get("authentication_status"):
    st.warning("Please log in first.")
    st.stop()
USER_ID = st.session_state["username"]
medicationScheduleManager = MedicationScheduleManager(USER_ID)
medication_tracker = medicationScheduleManager.return_medication_info()
if "page_config_set" not in st.session_state:
    st.set_page_config(
        page_title="NAIA assistant",
        page_icon="assets/Naia window icon.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state.page_config_set = True
st.title(":orange[NAIA - My Medication]")
st.subheader("Here's a summary of your Medication tracking")

if not medication_tracker:
    st.info("No medication tracking data available.")
    st.stop()

# df = pd.DataFrame(medication_tracker)
df = pd.DataFrame(medication_tracker)
df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
zn = ZoneInfo("Europe/London")
today = datetime.now(zn).date()

# Separate past and current/future data

past_df = df[df["datetime"].dt.date < today].copy()
future_df = df[df["datetime"].dt.date >= today].copy()

past_df = past_df.drop(columns=["_id"], errors="ignore")
future_df = future_df.drop(columns=["_id"], errors="ignore")

# To preserve past dates, show "taken_status" column
past_df["taken_status"] = past_df["taken"].apply(lambda x: "✅" if x else "❌")
past_df_display = past_df[["date", "time", "med_name", "dose", "frequency", "taken_status"]]


st.subheader("Medication for Today and Upcoming Days")

future_df = future_df.sort_values(by="datetime")
if future_df.empty:
    st.write("No medications scheduled for today or future dates.")
else:
    gb = GridOptionsBuilder.from_dataframe(future_df.drop(columns=["datetime"], errors='ignore'))
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_selection('single')
    gb.configure_column("taken", editable=True, cellEditor='agCheckboxCellEditor', cellEditorParams={"trueValue": True, "falseValue": False})
    gb.configure_column("date", editable=False)
    gb.configure_column("time", editable=False)
    gb.configure_default_column(editable=False)
    gb.configure_column("id", hide=True)
    gb.configure_column("patient_id", hide=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        future_df.drop(columns=["datetime"]),
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        theme='balham',
        height=400,
        fit_columns_on_grid_load=True,
    )

    updated_df = grid_response['data']

    if st.button("Save Changes"):
        updated_tracker = pd.concat([past_df, pd.DataFrame(updated_df)]).drop(columns=["taken_status", "datetime"], errors='ignore')
        updated_tracker = updated_tracker.sort_values(by=["date", "time"])
        # medicationScheduleManager.save_tracker(updated_tracker.to_dict(orient='records'))
        medicationScheduleManager.update_taken_status(updated_df.to_dict(orient='records'))
        st.success("Changes saved!")


past_df_display_sorted = past_df_display.sort_values(by=["date", "time"], ascending=False)

# Set up AgGrid for history
gb_past = GridOptionsBuilder.from_dataframe(past_df_display_sorted)
gb_past.configure_pagination(paginationAutoPageSize=True)
gb_past.configure_default_column(editable=False, sortable=True, filter=True, resizable=True)
grid_options_past = gb_past.build()

st.subheader("Medication History (Past Dates)")
AgGrid(
    past_df_display_sorted,
    gridOptions=grid_options_past,
    update_mode=GridUpdateMode.NO_UPDATE,
    allow_unsafe_jscode=True,
    theme='balham',
    height=300,
    fit_columns_on_grid_load=True,
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
