import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from app.RecoveryCheckUpScheduleManager import RecoveryCheckUpScheduleManager

if not st.session_state.get("authentication_status"):
    st.warning("Please log in first.")
    st.stop()

USER_ID = st.session_state["username"]
recoveryCheckUpScheduleManager = RecoveryCheckUpScheduleManager(USER_ID)
routine_tracker = recoveryCheckUpScheduleManager.return_routine_info()

# Page config
if "page_config_set" not in st.session_state:
    st.set_page_config(
        page_title="NAIA - Routine",
        page_icon="assets/Naia window icon.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state.page_config_set = True

st.title(":orange[NAIA - My Recovery Routine]")
st.subheader("Here's your physical recovery plan")

if not routine_tracker:
    st.info("No routine tracking data available.")
    st.stop()

df = pd.DataFrame(routine_tracker)
# Filter activities ongoing and programed
ongoing_df = df[df["is_ongoing"] == True].copy()
scheduled_df = df[df["is_ongoing"] != True].copy()



scheduled_df["datetime"] = pd.to_datetime(scheduled_df["date"] + " " + scheduled_df["time"])

if not ongoing_df.empty:
    with st.expander("📝 Ongoing Recommendations (No specific schedule)", expanded=True):
        for _, row in ongoing_df.iterrows():
            extra_info = []
            # Condicionales para añadir info si existe y es relevante
            if row.get("total_days"):
                extra_info.append(f"**Days:** {row['total_days']}")
            if row.get("frequency_per_day"):
                extra_info.append(f"**Frequency/day:** {row['frequency_per_day']}")
            if row.get("duration_minutes"):
                extra_info.append(f"**Duration:** {row['duration_minutes']} min")
            if row.get("preferred_times"):
                times = ", ".join(row["preferred_times"])
                extra_info.append(f"**Preferred times:** {times}")
            # Construcción del texto final
            details = " | ".join(extra_info)
            notes = row.get("notes", "")
            st.markdown(f"- **{row['activity']}**: {notes}{'  \n' + details if details else ''}")

today = datetime.now().date()
past_df = scheduled_df[scheduled_df["datetime"].dt.date < today].copy()
future_df = scheduled_df[scheduled_df["datetime"].dt.date >= today].copy()

past_df = past_df.drop(columns=["_id"], errors="ignore")
future_df = future_df.drop(columns=["_id"], errors="ignore")

columns_to_exclude = ["is_ongoing", "total_days", "preferred_times", "frequency", "type"]
future_df = future_df.drop(columns=[col for col in columns_to_exclude if col in future_df.columns], errors="ignore")

past_df["completed_status"] = past_df["completed"].apply(lambda x: "✅" if x else "❌")
past_df_display = past_df[["activity", "date", "time", "duration_minutes", "completed_status"]]

st.subheader("Today's and Upcoming Routine Tasks")
if future_df.empty:
    st.write("No scheduled routines.")
else:
    gb = GridOptionsBuilder.from_dataframe(future_df.drop(columns=["datetime"]))
    gb.configure_pagination()
    gb.configure_selection("single")
    gb.configure_column("completed", editable=True, cellEditor='agCheckboxCellEditor')
    gb.configure_column("id", hide=True)
    gb.configure_column("patient_id", hide=True)
    gb.configure_default_column(editable=False)
    grid_options = gb.build()

    grid_response = AgGrid(
        future_df.drop(columns=["datetime"]),
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        theme="balham",
        height=400,
        fit_columns_on_grid_load=False,  # 👈 Esto evita que las columnas se aplasten para caber
        width='100%'
        # fit_columns_on_grid_load=True,
    )

    updated_df = grid_response["data"]
    
    if st.button("Save Routine Changes"):
        updated_tracker = pd.concat([past_df, pd.DataFrame(updated_df)]).drop(columns=["completed_status", "datetime"], errors='ignore')
        updated_tracker = updated_tracker.sort_values(by=["date", "time"])
        # recoveryCheckUpScheduleManager.save_routine_tracker(updated_tracker.to_dict(orient="records"))
        recoveryCheckUpScheduleManager.update_completed_status(updated_df.to_dict(orient='records'))
        st.success("Routine tracker updated!")

# Historical
past_df_display_sorted = past_df_display.sort_values(by=["date", "time"], ascending=False)
gb_past = GridOptionsBuilder.from_dataframe(past_df_display_sorted)
gb_past.configure_pagination()
gb_past.configure_default_column(editable=False, sortable=True, filter=True)
grid_options_past = gb_past.build()

st.subheader("Routine History")
AgGrid(
    past_df_display_sorted,
    gridOptions=grid_options_past,
    update_mode=GridUpdateMode.NO_UPDATE,
    allow_unsafe_jscode=True,
    theme="balham",
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
