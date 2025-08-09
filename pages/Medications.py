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

# history_file = f"data/history_{USER_ID}.json"
# tracker_file = f"data/medicationTracker_{USER_ID}.json"

medicationScheduleManager = MedicationScheduleManager(USER_ID)

# frequency_schedule = {
#     "6x/day": [time(6, 0), time(10, 0), time(14, 0), time(18, 0), time(22, 0), time(2, 0)],
#     "5x/day": [time(7, 0), time(11, 0), time(15, 0), time(19, 0), time(23, 0)],
#     "4x/day": [time(8, 0), time(12, 0), time(16, 0), time(20, 0)],
#     "3x/day": [time(8, 0), time(14, 0), time(20, 00)],
#     "2x/day": [time(9, 0), time(21, 0)],
#     "1x/day": [time(9, 0)],
# }

# def create_tracker_from_history(history_path, tracker_path):
#     with open(history_path, "r", encoding="utf-8") as f:
#         data = json.load(f)
#     medications = data.get("medications", [])
#     surgery_date_str = data.get("surgery_date", None)
#     start_date = datetime.strptime(surgery_date_str, "%Y-%m-%d") if surgery_date_str else datetime.now()

#     tracker = []
#     for med in medications:
#         duration_str = med.get("duration", "7 days")
#         days = int(duration_str.split()[0])
#         freq = med.get("frequency", "").lower()
#         scheduled_times = frequency_schedule.get(freq, [time(9,0)])

#         for day_offset in range(days):
#             day_date = start_date + timedelta(days=day_offset)
#             day_str = day_date.strftime("%Y-%m-%d")
#             for t in scheduled_times:
#                 time_str = t.strftime("%H:%M")
#                 tracker.append({
#                     "date": day_str,
#                     "time": time_str,
#                     "med_name": med.get("name"),
#                     "dose": med.get("dose"),
#                     "frequency": med.get("frequency"),
#                     "taken": False
#                 })

#     with open(tracker_path, "w", encoding="utf-8") as f:
#         json.dump(tracker, f, indent=2)

#     return tracker

# def save_tracker(tracker):
#     with open(tracker_file, "w", encoding="utf-8") as f:
#         json.dump(tracker, f, indent=2)

# def load_tracker():
#     with open(tracker_file, "r", encoding="utf-8") as f:
#         return json.load(f)

# if os.path.exists(tracker_file):
#     medication_tracker = medicationScheduleManager.load_tracker()
# else:
#     medication_tracker = medicationScheduleManager.create_tracker_from_history(history_file, tracker_file)
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

df = pd.DataFrame(medication_tracker)
df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])

today = datetime.now().date()

# Separar datos pasados y actuales/futuros
past_df = df[df["datetime"].dt.date < today].copy()
future_df = df[df["datetime"].dt.date >= today].copy()

# Para fechas pasadas, mostrar columna "taken_status"
past_df["taken_status"] = past_df["taken"].apply(lambda x: "✅" if x else "❌")
past_df_display = past_df[["date", "time", "med_name", "dose", "frequency", "taken_status"]]


st.subheader("Medication for Today and Upcoming Days")

future_df = future_df.sort_values(by="datetime")
if future_df.empty:
    st.write("No medications scheduled for today or future dates.")
else:
    gb = GridOptionsBuilder.from_dataframe(future_df.drop(columns=["datetime"]))
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_selection('single')
    # Solo la columna "taken" editable aquí
    gb.configure_column("taken", editable=True, cellEditor='agCheckboxCellEditor', cellEditorParams={"trueValue": True, "falseValue": False})
    gb.configure_column("date", editable=False)
    gb.configure_column("time", editable=False)
    gb.configure_default_column(editable=False)
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
        medicationScheduleManager.save_tracker(updated_tracker.to_dict(orient='records'))
        st.success("Changes saved!")


#st.subheader("Medication History (Past Dates)")
#st.table(past_df_display)  # solo mostrar tabla simple sin edición



# Ordenar por fecha y hora descendente (más recientes primero)
past_df_display_sorted = past_df_display.sort_values(by=["date", "time"], ascending=False)

# Configurar AgGrid para historial
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
