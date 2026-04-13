import streamlit as st
import random
import time
import pandas as pd

st.set_page_config(
    page_title="Smart Wheelchair – EMG Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

defaults = {
    "running": False,
    "emg_data": [],
    "gesture_data": [],
    "last_value": 0,
    "last_gesture": "NONE",
    "last_action": "STOP",
    "analysis_snapshot": None,
    "snapshot_at": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def analyze_muscle(emg_values):
    if not emg_values or len(emg_values) < 5:
        return None
    avg         = sum(emg_values) / len(emg_values)
    peak        = max(emg_values)
    variability = max(emg_values) - min(emg_values)
    if avg < 1200:
        return {
            "condition": "🔵 Weak Muscle Activity", "color": "blue",
            "note": "Muscles show low electrical activity. Gentle rehabilitation recommended.",
            "exercises": ["Hand grip squeezes – 3 × 10", "Finger extension stretches",
                          "Wrist rotation – 2 min each side", "Light resistance band pulls"]
        }
    elif avg < 2000:
        if variability > 800:
            return {
                "condition": "🟡 Irregular Activity", "color": "orange",
                "note": "Uneven signals detected. Focus on slow, controlled movements.",
                "exercises": ["Slow controlled arm raises", "Isometric holds – 10 sec each",
                              "Rhythmic fist open/close", "Breathing + light movement"]
            }
        return {
            "condition": "🟢 Normal Activity", "color": "green",
            "note": "Muscle health looks good. Maintain your routine.",
            "exercises": ["Continue current physio routine", "Light cardio if mobility permits",
                          "Stay hydrated and rest well"]
        }
    else:
        if peak > 2800:
            return {
                "condition": "🔴 High Strain / Fatigue", "color": "red",
                "note": "Muscles showing signs of overexertion. Rest is essential.",
                "exercises": ["Complete rest – 20 to 30 min", "Cold compress on active muscle",
                              "Gentle passive stretching only", "Elevate limb if swollen"]
            }
        return {
            "condition": "🟠 Elevated Strain", "color": "orange",
            "note": "Moderate strain detected. Reduce intensity and monitor.",
            "exercises": ["Reduce reps by 50%", "Slow down movement speed",
                          "Add rest intervals", "Consult physio if it persists"]
        }

def decide_action(emg_value, gesture, low_thresh, high_thresh):
    if emg_value < low_thresh:
        return "STOP"
    if gesture == "FORWARD":   return "MOVE FORWARD"
    elif gesture == "LEFT":    return "TURN LEFT"
    elif gesture == "RIGHT":   return "TURN RIGHT"
    elif gesture == "BACKWARD": return "MOVE BACKWARD"
    else:
        return "FAST FORWARD" if emg_value >= high_thresh else "MOVE FORWARD"

st.sidebar.title("⚙️ Controls")
mode = st.sidebar.radio("Data Source", ["🔵 Simulation", "🟢 Real EMG"])
st.sidebar.markdown("---")
LOW_THRESHOLD  = st.sidebar.slider("Low Threshold (Stop zone)",  800,  2000, 1200, step=50)
HIGH_THRESHOLD = st.sidebar.slider("High Threshold (Fast zone)", 1500, 3500, 2000, step=50)
st.sidebar.markdown("---")

btn_col1, btn_col2 = st.sidebar.columns(2)
with btn_col1:
    if st.button("▶ Start" if not st.session_state.running else "▶ Resume"):
        st.session_state.running = True
with btn_col2:
    if st.button("⏸ Stop"):
        st.session_state.running = False

ser = None
if "Real EMG" in mode:
    import importlib
    if importlib.util.find_spec("serial"):
        import serial
        port = st.sidebar.text_input("Serial Port", value="COM3")
        try:
            ser = serial.Serial(port, 115200, timeout=0.1)
            st.sidebar.success(f"✅ Connected to {port}")
        except Exception:
            st.sidebar.error(f"❌ Cannot open {port}")
    else:
        st.sidebar.warning("Run: pip install pyserial")

st.title("Smart Wheelchair – EMG Control Dashboard")
st.caption("Human-Machine Interface | EMG + Gesture Hybrid Control System")
status_ph = st.empty()

c1, c2, c3 = st.columns(3)
emg_ph     = c1.empty()
gesture_ph = c2.empty()
action_ph  = c3.empty()
st.markdown("---")

graph_col, rec_col = st.columns([6, 4])
with graph_col:
    st.markdown("Live EMG Signal")
    chart_ph = st.empty()
with rec_col:
    st.markdown("Muscle Recovery Summary")
    rec_ph = st.empty()

st.markdown("---")
dl_ph = st.empty()

SNAPSHOT_EVERY = 30

def render_ui():
    v  = st.session_state.last_value
    g  = st.session_state.last_gesture
    a  = st.session_state.last_action
    dd = st.session_state.emg_data
    n  = len(dd)

    if st.session_state.running:
        status_ph.success("🟢 System Running")
    else:
        status_ph.warning("🟡 Paused – press ▶ to resume")

    emg_ph.metric("⚡ EMG Value", v)
    gesture_ph.metric("🖐 Gesture", g)
    if a == "STOP":            action_ph.error(f"🛑 {a}")
    elif "FORWARD" in a:       action_ph.success(f"⬆️ {a}")
    elif "LEFT" in a:          action_ph.warning(f"↩️ {a}")
    elif "RIGHT" in a:         action_ph.warning(f"↪️ {a}")
    elif "BACKWARD" in a:      action_ph.error(f"⬇️ {a}")
    else:                      action_ph.info(f"ℹ️ {a}")

    if dd:
        chart_ph.line_chart(pd.DataFrame({"EMG Signal": dd}), height=320)

    if n < 10:
        rec_ph.info(f"Collecting data… {n}/10 samples needed")
    else:
        if (st.session_state.analysis_snapshot is None or
                n - st.session_state.snapshot_at >= SNAPSHOT_EVERY):
            st.session_state.analysis_snapshot = analyze_muscle(dd)
            st.session_state.snapshot_at = n

        snap        = st.session_state.analysis_snapshot
        next_update = SNAPSHOT_EVERY - (n - st.session_state.snapshot_at)

        if snap:
            border = {"green": "#4ade80", "red": "#f87171",
                      "orange": "#fb923c", "blue": "#60a5fa"}.get(snap["color"], "#888")
            exercises_html = "".join(
                f'<p style="font-size:0.82rem;color:#c4c4d4;margin:3px 0">• {ex}</p>'
                for ex in snap["exercises"]
            )
            rec_ph.markdown(f"""
                <div style="background:#1a1a2e;border-radius:14px;padding:18px 20px;
                            border-left:5px solid {border};">
                    <p style="font-size:1.05rem;font-weight:700;margin:0 0 6px 0;color:#f0f0f0">
                        {snap['condition']}</p>
                    <p style="font-size:0.82rem;color:#a0a0b8;margin:0 0 10px 0;line-height:1.4">
                        {snap['note']}</p>
                    <p style="font-size:0.75rem;color:#60a5fa;margin:0 0 10px 0">
                        🔁 Next update in ~{next_update} samples</p>
                    <hr style="border:none;border-top:1px solid #2e2e44;margin:8px 0 10px 0"/>
                    <p style="font-size:0.85rem;font-weight:600;color:#d1d5db;margin:0 0 6px 0">
                        Suggested Exercises</p>
                    {exercises_html}
                </div>""", unsafe_allow_html=True)

    if dd:
        dl_ph.download_button("📥 Download Session Data (CSV)",
            pd.DataFrame({"emg": dd}).to_csv(index=False),
            "emg_session_data.csv", mime="text/csv")

GESTURES = ["FORWARD", "LEFT", "RIGHT", "BACKWARD", "NONE"]

if st.session_state.running:
    value   = None
    gesture = "NONE"

    if "Simulation" in mode:
        base    = 1400 + 400 * (len(st.session_state.emg_data) % 20 - 10) / 10
        value   = int(base + random.gauss(0, 150))
        value   = max(700, min(3000, value))
        gesture = random.choices(GESTURES, weights=[40, 15, 15, 10, 20])[0]

    elif "Real EMG" in mode:
        if ser:
            try:
                raw = ser.readline().decode("utf-8", errors="ignore").strip()
                if "EMG:" in raw:
                    parts   = raw.split(",")
                    value   = int(parts[0].split(":")[1])
                    if len(parts) > 1 and "GESTURE:" in parts[1]:
                        gesture = parts[1].split(":")[1].strip().upper()
            except Exception as e:
                st.session_state.running = False
                st.warning(f"Serial error: {e}")
        else:
            st.session_state.running = False
            st.warning("No serial connection. Switch to Simulation or connect device.")

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
    render_ui()
