import json
import logging

import pandas as pd
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db


st.set_page_config(
    page_title="Smart Lecture Room Dashboard",
    page_icon="⚡",
    layout="wide",
)

st.title("🎓 Smart Lecture Room Dashboard")


@st.cache_resource
def get_firebase_app():
    try:
        return firebase_admin.get_app("lecture_room_dashboard")
    except ValueError:
        service_account = json.loads(
            st.secrets["FIREBASE_SERVICE_ACCOUNT_JSON"]
        )
        credential = credentials.Certificate(service_account)

        return firebase_admin.initialize_app(
            credential,
            {"databaseURL": st.secrets["FIREBASE_DATABASE_URL"]},
            name="lecture_room_dashboard",
        )


def show_state(value):
    if value is True:
        return "On"
    if value is False:
        return "Off"
    return "—"


@st.fragment(run_every="5s")
def show_dashboard():
    try:
        app = get_firebase_app()
        room = db.reference("rooms/lecture_room_1", app=app)
        current = room.child("current").get()
        history = (
            room.child("history")
            .order_by_key()
            .limit_to_last(100)
            .get()
        )
    except Exception:
        logging.exception("Could not read Firebase")
        st.error("Could not read Firebase. Check the app Secrets and logs.")
        return

    if not isinstance(current, dict):
        st.info("Waiting for real sensor readings from the Raspberry Pi.")
        return

    st.caption(f"Last reading: {current.get('timestamp', 'Unknown')}")

    occupied_values = [
        current.get(f"zone{zone}_occupied")
        for zone in range(1, 5)
    ]
    if any(value is True for value in occupied_values):
        room_status = "Occupied"
    elif all(value is False for value in occupied_values):
        room_status = "Empty"
    else:
        room_status = "Unknown"

    temperature = current.get("temperature_c")
    humidity = current.get("humidity_percent")

    col1, col2, col3 = st.columns(3)
    col1.metric("Room occupancy", room_status)
    col2.metric(
        "Temperature",
        f"{temperature:.1f} °C"
        if isinstance(temperature, (int, float)) else "—",
    )
    col3.metric(
        "Humidity",
        f"{humidity:.1f} %"
        if isinstance(humidity, (int, float)) else "—",
    )

    st.subheader("Four zones")
    zone_rows = []
    for zone in range(1, 5):
        zone_rows.append({
            "Zone": zone,
            "Motion": show_state(current.get(f"zone{zone}_motion")),
            "Occupied": show_state(
                current.get(f"zone{zone}_occupied")
            ),
            "LDR voltage (V)": current.get(f"zone{zone}_light_v"),
            "Bright": show_state(current.get(f"zone{zone}_bright")),
            "LED": show_state(current.get(f"zone{zone}_led_on")),
        })
    st.dataframe(pd.DataFrame(zone_rows), hide_index=True)

    st.subheader("Equipment")
    fan1, fan2, motor = st.columns(3)
    fan1.metric("Fan 1", show_state(current.get("fan1_on")))
    fan2.metric("Fan 2", show_state(current.get("fan2_on")))
    motor.metric("AC motor", show_state(current.get("ac_motor_on")))

    if isinstance(history, dict) and history:
        records = [
            record for record in history.values()
            if isinstance(record, dict)
        ]
        if records:
            df = pd.DataFrame(records)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(
                    df["timestamp"], errors="coerce", utc=True
                )
                df = df.dropna(subset=["timestamp"])
                df = df.sort_values("timestamp")

                st.subheader("History")
                for column, title in [
                    ("temperature_c", "Temperature (°C)"),
                    ("humidity_percent", "Humidity (%)"),
                ]:
                    if column in df.columns:
                        st.write(title)
                        st.line_chart(
                            df.set_index("timestamp")[[column]]
                        )

                light_columns = [
                    f"zone{zone}_light_v" for zone in range(1, 5)
                ]
                available = [
                    column for column in light_columns
                    if column in df.columns
                ]
                if available:
                    st.write("LDR voltage by zone (V)")
                    st.line_chart(
                        df.set_index("timestamp")[available]
                    )

                st.subheader("Recent readings")
                st.dataframe(df.sort_values(
                    "timestamp", ascending=False
                ), hide_index=True)


show_dashboard()