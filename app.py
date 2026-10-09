import json
import logging
from datetime import datetime, timezone

import firebase_admin
import pandas as pd
import streamlit as st
from firebase_admin import credentials, db


st.set_page_config(
    page_title="Smart Lecture Room Dashboard",
    page_icon="⚡",
    layout="wide",
)

st.title("🎓 Smart Lecture Room")
st.caption(
    "Temperature, humidity, occupancy, and lighting across four zones. "
    "The page refreshes every 5 seconds."
)


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
    return "Unknown"


def show_occupancy(value):
    if value is True:
        return "Occupied"
    if value is False:
        return "Empty"
    return "Unknown"


def show_motion(value):
    if value is True:
        return "Detected"
    if value is False:
        return "None"
    return "Unknown"


def show_brightness(value):
    if value is True:
        return "Bright"
    if value is False:
        return "Dark"
    return "Unknown"


def reading_age_seconds(timestamp):
    if not isinstance(timestamp, str):
        return None

    try:
        reading_time = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )
    except ValueError:
        return None

    if reading_time.tzinfo is None:
        return None

    return (
        datetime.now(timezone.utc)
        - reading_time.astimezone(timezone.utc)
    ).total_seconds()


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
        st.error(
            "Could not read Firebase. Check the app Secrets and logs."
        )
        return

    if not isinstance(current, dict):
        with st.container(border=True):
            st.info(
                "Waiting for real sensor readings from the Raspberry Pi."
            )
            st.write(
                "The dashboard will display room status here when "
                "the Raspberry Pi starts sending data."
            )
        return

    last_updated = current.get("timestamp")
    age = reading_age_seconds(last_updated)

    st.caption(f"Last updated: {last_updated or 'Unknown'}")

    if age is None or age < -30:
        st.warning(
            "Cannot verify when the last reading was taken. "
            "Check the Raspberry Pi clock."
        )
    elif age > 30:
        st.warning(
            f"Sensor data is {int(age)} seconds old. "
            "The Raspberry Pi may be offline."
        )
    else:
        st.success("Sensor data is up to date.")

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

    temperature_text = (
        f"{temperature:.1f} °C"
        if isinstance(temperature, (int, float))
        else "—"
    )
    humidity_text = (
        f"{humidity:.1f} %"
        if isinstance(humidity, (int, float))
        else "—"
    )

    st.subheader("Room overview")
    overview_columns = st.columns(3)

    with overview_columns[0]:
        with st.container(border=True):
            st.metric("Room occupancy", room_status)

    with overview_columns[1]:
        with st.container(border=True):
            st.metric("Temperature", temperature_text)

    with overview_columns[2]:
        with st.container(border=True):
            st.metric("Humidity", humidity_text)

    st.subheader("Four zones")
    zone_columns = st.columns(4)

    for zone, column in enumerate(zone_columns, start=1):
        with column:
            with st.container(border=True):
                st.markdown(f"#### Zone {zone}")
                st.metric(
                    "Occupancy",
                    show_occupancy(
                        current.get(f"zone{zone}_occupied")
                    ),
                )

                voltage = current.get(f"zone{zone}_light_v")
                voltage_text = (
                    f"{voltage:.2f} V"
                    if isinstance(voltage, (int, float))
                    else "—"
                )

                st.write(
                    "**Motion:** "
                    + show_motion(
                        current.get(f"zone{zone}_motion")
                    )
                )
                st.write(f"**LDR reading:** {voltage_text}")
                st.write(
                    "**Ambient light:** "
                    + show_brightness(
                        current.get(f"zone{zone}_bright")
                    )
                )
                st.write(
                    "**LED:** "
                    + show_state(
                        current.get(f"zone{zone}_led_on")
                    )
                )

    st.subheader("Equipment")
    equipment_columns = st.columns(3)

    with equipment_columns[0]:
        with st.container(border=True):
            st.metric(
                "Fan 1",
                show_state(current.get("fan1_on")),
            )

    with equipment_columns[1]:
        with st.container(border=True):
            st.metric(
                "Fan 2",
                show_state(current.get("fan2_on")),
            )

    with equipment_columns[2]:
        with st.container(border=True):
            st.metric(
                "AC motor",
                show_state(current.get("ac_motor_on")),
            )

    if not isinstance(history, dict) or not history:
        st.info("History graphs will appear after readings are saved.")
        return

    records = [
        record
        for record in history.values()
        if isinstance(record, dict)
    ]

    if not records:
        return

    df = pd.DataFrame(records)

    if "timestamp" not in df.columns:
        return

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
        utc=True,
    )
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values("timestamp")

    if df.empty:
        return

    st.subheader("History")

    if "temperature_c" in df.columns:
        st.write("Temperature (°C)")
        st.line_chart(
            df.set_index("timestamp")[["temperature_c"]]
        )

    if "humidity_percent" in df.columns:
        st.write("Humidity (%)")
        st.line_chart(
            df.set_index("timestamp")[["humidity_percent"]]
        )

    light_columns = [
        f"zone{zone}_light_v"
        for zone in range(1, 5)
        if f"zone{zone}_light_v" in df.columns
    ]

    if light_columns:
        st.write("LDR voltage by zone (V)")
        light_data = df.set_index("timestamp")[light_columns]
        light_data = light_data.rename(
            columns={
                f"zone{zone}_light_v": f"Zone {zone}"
                for zone in range(1, 5)
            }
        )
        st.line_chart(light_data)

    st.subheader("Recent readings")
    st.dataframe(
        df.sort_values("timestamp", ascending=False),
        hide_index=True,
    )


show_dashboard()