import pandas as pd
import streamlit as st

# Configure the page layout
st.set_page_config(
    page_title="Smart Lecture Room Dashboard", page_icon="⚡", layout="wide"
)

st.title("🎓 Smart Energy Efficiency & Automated Control System")
st.markdown(
    "Live monitoring dashboard for university"
    " lecture rooms."
)


# --- MOCK DATA (Fake data so you can build the UI without a database) ---
def get_mock_data():
  data = {
      "timestamp": [
          "2026-10-07 13:00:00",
          "2026-10-07 12:55:00",
          "2026-10-07 12:50:00",
          "2026-10-07 12:45:00",
          "2026-10-07 12:40:00",
      ],
      "occupancy": [1, 1, 0, 0, 1],
      "temperature": [28.5, 29.0, 27.5, 26.8, 28.1],
      "humidity": [60.0, 62.0, 58.0, 55.0, 59.0],
      "light_intensity": [350.0, 400.0, 120.0, 90.0, 310.0],
      "energy_consumption": [120.5, 135.0, 15.0, 12.5, 118.0],
  }
  df = pd.DataFrame(data)
  # Convert timestamp to actual datetime so charts format it cleanly
  df["timestamp"] = pd.to_datetime(df["timestamp"])
  return df

df = get_mock_data()
latest = df.iloc[0]

# --- SECTION 1: REAL-TIME METRICS ---
st.subheader("🔴 Live Room Status (Mock View)")
col1, col2, col3, col4 = st.columns(4)

with col1:
  occupancy_text = "Occupied 🟢" if latest["occupancy"] == 1 else "Empty 🔴"
  st.metric(
      label="Room Occupancy", value=occupancy_text, help="Detected via PIR sensor"
  )

with col2:
  st.metric(
      label="Temperature",
      value=f"{latest['temperature']} °C",
      help="Temperature & Humidity sensor",
  )

with col3:
  st.metric(
      label="Light Intensity",
      value=f"{latest['light_intensity']} lux",
      help="Measured via LDR sensor",
  )

with col4:
  st.metric(
      label="Current Power",
      value=f"{latest['energy_consumption']} W",
      help="Active electrical load",
  )

# --- SECTION 2: EQUIPMENT CONTROL PANEL ---
st.subheader("⚙️ Controlled Equipment Status")
eq_col1, eq_col2 = st.columns(2)
with eq_col1:
  st.info("**Lighting System:** Auto-ON (Low Ambient Light)")
with eq_col2:
  st.info("**AC / Fans:** Regulated based on occupancy")

# --- SECTION 3: ENERGY ANALYTICS & TRENDS ---
st.subheader("📈 Energy Consumption Over Time")
st.line_chart(df, x="timestamp", y="energy_consumption")

# --- SECTION 4: HISTORICAL DATA TABLE ---
st.subheader("📋 Raw Sensor Logs")
st.dataframe(df, use_container_width=True)