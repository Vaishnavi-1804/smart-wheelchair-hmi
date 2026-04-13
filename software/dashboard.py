import streamlit as st
import random
import time
import pandas as pd

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Wheelchair – EMG Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# SESSION STATE INIT  (always at top, before any logic)
# ──────────────────────────────────────────────
if "running" not in st.session_state:
    st.session_state.running = False
if "emg_data" not in st.session_state:
    st.session_state.emg_data = []
if "gesture_data" not in st.session_state:
    st.session_state.gesture_data = []
if "last_value" not in st.session_state:
    st.session_state.last_value = 0
if "last_gesture" not in st.session_state:
    st.session_state.last_gesture = "NONE"
if "last_action" not in st.session_state:
    st.session_state.last_action = "STOP"

# ──────────────────────────────────────────────
# MUSCLE ANALYSIS  (separate logic, no side effects)
# ──────────────────────────────────────────────
def analyze_muscle(emg_values):
    """Analyse EMG values and return (condition, recommendation, exercises)."""
    if not emg_values or len(emg_values) < 5:
        return "Insufficient Data", "Collect more data for analysis.", []

    avg   = sum(emg_values) / len(emg_values)
    peak  = max(emg_values)
    variability = max(emg_values) - min(emg_values)

    if avg < 1200:
        return (
            "🔵 Weak Muscle Activity",
            "Muscles show low electrical activity. Gentle rehabilitation recommended.",
            [
                "Hand grip squeezes – 3 sets of 10",
                "Finger extension stretches",
                "Wrist rotation – 2 mins each direction",
                "Light resistance band pulls"
            ]
        )
    elif avg < 2000:
        if variability > 800:
            return (
                "🟡 Irregular Activity Detected",
                "Muscle activity is uneven. Focus on controlled, steady movements.",
                [
                    "Slow, controlled arm raises",
                    "Isometric holds – 10 sec each",
                    "Rhythmic opening/closing of fist",
                    "Breathing exercises combined with light movement"
                ]
            )
        return (
            "🟢 Normal Muscle Activity",
            "Muscle health looks good. Maintain your current routine.",
            [
                "Continue current physiotherapy routine",
                "Light cardio if mobility permits",
                "Maintain hydration and rest cycles"
            ]
        )
    else:
        if peak > 2800:
            return (
                "🔴 High Strain / Possible Fatigue",
                "Muscles are showing signs of overexertion. Rest is essential.",
                [
                    "Complete rest for 20–30 minutes",
                    "Cold compress on active muscle group",
                    "Gentle passive stretching (no resistance)",
                    "Elevation of limb if swollen"
                ]
            )
        return (
            "🟠 Elevated Muscle Strain",
            "Moderate strain detected. Reduce intensity and monitor.",
            [
                "Reduce repetitions by 50%",
                "Slow down movement speed",
                "Add rest intervals between exercises",
                "Consult physiotherapist if persists"
            ]
        )

# ──────────────────────────────────────────────
# DECISION LOGIC
# ──────────────────────────────────────────────
def decide_action(emg_value, gesture, low_thresh, high_thresh):
    if emg_value < low_thresh:
        return "STOP"
    if gesture == "FORWARD":
        return "MOVE FORWARD"
    elif gesture == "LEFT":
        return "TURN LEFT"
    elif gesture == "RIGHT":
        return "TURN RIGHT"
    elif gesture == "BACKWARD":
        return "MOVE BACKWARD"
    else:
        if emg_value >= high_thresh:
            return "FAST FORWARD"
        return "MOVE FORWARD"

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
st.sidebar.title("⚙️ Controls")

mode = st.sidebar.radio("Data Source", ["🔵 Simulation", "🟢 Real EMG"])

st.sidebar.markdown("---")
LOW_THRESHOLD  = st.sidebar.slider("Low Threshold (Stop zone)",  800,  2000, 1200, step=50)
HIGH_THRESHOLD = st.sidebar.slider("High Threshold (Fast zone)", 1500, 3500, 2000, step=50)
st.sidebar.markdown("---")

col_s, col_p = st.sidebar.columns(2)
with col_s:
    if st.button("▶ Start" if not st.session_state.running else "▶ Resume"):
        st.session_state.running = True
with col_p:
    if st.button("⏸ Stop"):
        st.session_state.running = False

# Serial setup (only attempted in Real EMG mode)
ser = None
if "Real EMG" in mode:
    import importlib
    serial_spec = importlib.util.find_spec("serial")
    if serial_spec:
        import serial
        port = st.sidebar.text_input("Serial Port", value="COM3")
        try:
            ser = serial.Serial(port, 115200, timeout=0.1)
            st.sidebar.success(f"✅ Connected to {port}")
        except Exception:
            st.sidebar.error(f"❌ Cannot open {port}")
    else:
        st.sidebar.warning("pyserial not installed. Run: pip install pyserial")

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.title("Smart Wheelchair – EMG Control Dashboard")
st.caption("Human-Machine Interface | EMG + Gesture Hybrid Control System")

status_placeholder = st.empty()

# ──────────────────────────────────────────────
# MAIN LAYOUT  (3 metric columns)
# ──────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
emg_metric     = c1.empty()
gesture_metric = c2.empty()
action_metric  = c3.empty()

st.markdown("---")

# Chart
chart_placeholder = st.empty()

st.markdown("---")

# Recovery section
recovery_placeholder = st.empty()

# Download
download_placeholder = st.empty()

# ──────────────────────────────────────────────
# RENDER HELPER  (called every loop + on idle)
# ──────────────────────────────────────────────
def render_ui():
    v  = st.session_state.last_value
    g  = st.session_state.last_gesture
    a  = st.session_state.last_action
    dd = st.session_state.emg_data

    # Status bar
    if st.session_state.running:
        status_placeholder.success("🟢 System Running")
    else:
        status_placeholder.warning("🟡 System Paused – press ▶ to resume")

    # Metrics
    emg_metric.metric("⚡ EMG Value", v, delta=None)
    gesture_metric.metric("🖐 Gesture", g)

    if a == "STOP":
        action_metric.error(f"🛑 {a}")
    elif "FORWARD" in a:
        action_metric.success(f"⬆️ {a}")
    elif "LEFT" in a:
        action_metric.warning(f"↩️ {a}")
    elif "RIGHT" in a:
        action_metric.warning(f"↪️ {a}")
    elif "BACKWARD" in a:
        action_metric.error(f"⬇️ {a}")
    else:
        action_metric.info(f"ℹ️ {a}")

    # Chart
    if dd:
        df_chart = pd.DataFrame({"EMG Signal": dd})
        chart_placeholder.line_chart(df_chart, height=250)

    # Muscle Recovery Analysis
    if len(dd) >= 10:
        condition, recommendation, exercises = analyze_muscle(dd)
        with recovery_placeholder.container():
            st.subheader("Muscle Recovery Analysis")
            rc1, rc2 = st.columns([1, 2])
            with rc1:
                st.markdown(f"**Condition:** {condition}")
                st.markdown(f"**Recommendation:** {recommendation}")
            with rc2:
                if exercises:
                    st.markdown("**Suggested Exercises:**")
                    for ex in exercises:
                        st.markdown(f"- {ex}")

    # Download button
    if dd:
        df_dl = pd.DataFrame({
            "emg": st.session_state.emg_data,
        })
        download_placeholder.download_button(
            label="📥 Download Session Data (CSV)",
            data=df_dl.to_csv(index=False),
            file_name="emg_session_data.csv",
            mime="text/csv"
        )

# ──────────────────────────────────────────────
# DATA FETCH + LOOP
# ──────────────────────────────────────────────
GESTURES = ["FORWARD", "LEFT", "RIGHT", "BACKWARD", "NONE"]

if st.session_state.running:
    value   = None
    gesture = "NONE"

    # ── Simulation ──────────────────────────────
    if "Simulation" in mode:
        # Realistic-ish wave: slowly rising then falling
        base = 1400 + 400 * (len(st.session_state.emg_data) % 20 - 10) / 10
        value   = int(base + random.gauss(0, 150))
        value   = max(700, min(3000, value))
        gesture = random.choices(
            GESTURES,
            weights=[40, 15, 15, 10, 20]  # FORWARD most likely
        )[0]

    # ── Real EMG ────────────────────────────────
    elif "Real EMG" in mode:
        if ser:
            try:
                raw = ser.readline().decode("utf-8", errors="ignore").strip()
                # Expected format:  EMG:1234  or  EMG:1234,GESTURE:LEFT
                if "EMG:" in raw:
                    parts = raw.split(",")
                    emg_part = parts[0]
                    value = int(emg_part.split(":")[1])
                    if len(parts) > 1 and "GESTURE:" in parts[1]:
                        gesture = parts[1].split(":")[1].strip().upper()
            except Exception as e:
                st.session_state.running = False
                st.warning(f"Serial error: {e}")
        else:
            st.session_state.running = False
            st.warning("No serial connection. Switch to Simulation or connect device.")

    # ── Store + render ───────────────────────────
    if value is not None:
        action = decide_action(value, gesture, LOW_THRESHOLD, HIGH_THRESHOLD)

        st.session_state.emg_data.append(value)
        st.session_state.emg_data = st.session_state.emg_data[-200:]

        st.session_state.last_value   = value
        st.session_state.last_gesture = gesture
        st.session_state.last_action  = action

    render_ui()

    time.sleep(0.15)
    st.rerun()

else:
    # Idle – just render last known state
    render_ui()
