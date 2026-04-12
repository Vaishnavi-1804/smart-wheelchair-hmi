import streamlit as st
import random
import time
import pandas as pd

if "running" not in st.session_state:
    st.session_state.running = False

if "data" not in st.session_state:
    st.session_state.data = []


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

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("▶ Start"):
        st.session_state.running = True

with col2:
    if st.button("⏸ Stop"):
        st.session_state.running = False

if st.session_state.running:

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

    st.session_state.data.append(value)
    st.session_state.data = st.session_state.data[-100:]

    time.sleep(0.1)
    st.rerun()
    
    # Store data
    if st.session_state.data:
        value = st.session_state.data[-1]
    else:
        value = 0
    
    # Decision logic
    if value < LOW_THRESHOLD:
        action = "STOP"
    elif value < HIGH_THRESHOLD:
        action = "MOVE FORWARD"
    else:
        action = "TURN / FAST"

    # Update UI
    value_box.metric("EMG Value", value)
    action_box.write(f"Action: {action}")
    chart.line_chart(st.session_state.data)

    
if st.session_state.data:
    df = pd.DataFrame({"emg": st.session_state.data})
    st.download_button("Download Data", df.to_csv(index=False), "emg_data.csv")
