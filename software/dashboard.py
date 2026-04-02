import streamlit as st
import random
import time

st.set_page_config(page_title="EMG Dashboard", layout="wide")

st.title("💪 EMG Signal Dashboard (Simulation Mode)")

# Thresholds
LOW_THRESHOLD = 1200
HIGH_THRESHOLD = 2000

# UI placeholders
value_box = st.empty()
action_box = st.empty()
chart = st.line_chart([0])

data = []

st.sidebar.header("Controls")
run = st.sidebar.checkbox("Start Simulation")

while run:
    # Simulated EMG signal
    value = random.randint(900, 2500)

    data.append(value)
    data = data[-100:]

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
    chart.line_chart(data)

    time.sleep(0.2)
