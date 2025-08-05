import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from app.RoutineScheduleManager import RoutineScheduleManager

if not st.session_state.get("authentication_status"):
    st.warning("Please log in first.")
    st.stop()

USER_ID = st.session_state["username"]
history_file = f"data/history_{USER_ID}.json"
routine_tracker_file = f"data/routineTracker_{USER_ID}.json"

def create_routine_tracker_from_history(history_path, routine_tracker_path):
    with open(history_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    routine_list = data.get("routine", [])
    surgery_date = data.get("surgery_date", datetime.now().strftime("%Y-%m-%d"))
    manager = RoutineScheduleManager(routine_list, start_date=surgery_date)
    routine_schedule = manager.create_routine_tracker_from_history(history_path, routine_tracker_path)
    print("schedule ", routine_schedule)
    with open(routine_tracker_path, "w", encoding="utf-8") as f:
        json.dump(routine_schedule, f, indent=2)
    return routine_schedule

def load_routine_tracker():
    with open(routine_tracker_file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_routine_tracker(data):
    with open(routine_tracker_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# Generate if doesn't exist
if not os.path.exists(routine_tracker_file):
    routine_tracker = create_routine_tracker_from_history(history_file, routine_tracker_file)
else:
    routine_tracker = load_routine_tracker()

# Page config
if "page_config_set" not in st.session_state:
    st.set_page_config(
        page_title="NAIA - Routine",
        page_icon="🧘‍♂️",
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
df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])

today = datetime.now().date()
past_df = df[df["datetime"].dt.date < today].copy()
future_df = df[df["datetime"].dt.date >= today].copy()

past_df["completed_status"] = past_df["completed"].apply(lambda x: "✅" if x else "❌")
#past_df_display = past_df[["date", "time", "task", "category", "duration_minutes", "completed_status"]]
past_df_display = past_df[["date", "time", "activity", "duration_minutes", "completed_status"]]


st.subheader("Today's and Upcoming Routine Tasks")

if future_df.empty:
    st.write("No scheduled routines.")
else:
    gb = GridOptionsBuilder.from_dataframe(future_df.drop(columns=["datetime"]))
    gb.configure_pagination()
    gb.configure_selection("single")
    gb.configure_column("completed", editable=True, cellEditor='agCheckboxCellEditor')
    gb.configure_default_column(editable=False)
    grid_options = gb.build()

    grid_response = AgGrid(
        future_df.drop(columns=["datetime"]),
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        theme="balham",
        height=400,
        fit_columns_on_grid_load=True,
    )

    updated_df = grid_response["data"]

    if st.button("Save Routine Changes"):
        updated_tracker = pd.concat([past_df, pd.DataFrame(updated_df)]).drop(columns=["completed_status", "datetime"], errors='ignore')
        updated_tracker = updated_tracker.sort_values(by=["date", "time"])
        save_routine_tracker(updated_tracker.to_dict(orient="records"))
        st.success("Routine tracker updated!")

# Historial
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
