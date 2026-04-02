import streamlit as st
import random
import time
import pandas as pd

st.set_page_config(page_title="EMG Dashboard", layout="wide")

st.title("EMG Signal Dashboard")

# Sidebar controls
mode = st.sidebar.radio("Select Mode", ["Simulation", "Real EMG"])

LOW_THRESHOLD = st.sidebar.slider("Low Threshold", 800, 2000, 1200)
HIGH_THRESHOLD = st.sidebar.slider("High Threshold", 1500, 3000, 2000)

# UI elements
value_box = st.empty()
action_box = st.empty()
chart = st.line_chart([0])

data = []

# Optional: serial setup (only used in real mode)
ser = None
if mode == "Real EMG":
    import serial
    try:
        ser = serial.Serial('COM3', 115200)
    except:
        st.error("Serial not connected")

run = st.sidebar.checkbox("Start")

if run:
    # Get value
    if mode == "Simulation":
        value = random.randint(900, 2500)

    elif mode == "Real EMG" and ser:
        line = ser.readline().decode().strip()
        if "EMG:" in line:
            try:
                value = int(line.split(":")[1])
            except:
                st.stop()
        else:
            st.stop()
    else:
        st.stop()

    # Store data
    if "data" not in st.session_state:
        st.session_state.data = []
    st.session_state.data.append(value)
    st.session_state.data = st.session_state.data[-100:]
    
    # Decision logic
    if value < LOW_THRESHOLD:
        action = "STOP"
    elif value < HIGH_THRESHOLD:
        action = "MOVE FORWARD"
    else:
        action = "TURN / FAST"

    # Update UI
    value_box.metric("EMG Value", value)
    action_box.success(f"Action: {action}")
    chart.line_chart(st.session_state.data)

    time.sleep(0.1)
    st.rerun()
    
if data:
    df = pd.DataFrame({"emg":data})
    st.download_button("Download Data", df.to_csv(index=False), "emg_data.csv")
