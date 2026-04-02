import serial
import pandas as pd
from datetime import datetime

# 🔧 Change this to your correct port
ser = serial.Serial('COM3', 115200)   # For Windows: COM3, COM4...
# For Mac/Linux use something like: '/dev/ttyUSB0' or '/dev/tty.SLAB_USBtoUART'

data = []

print("Recording started... Press Ctrl+C to stop")

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        print(line)

        # Expecting format: EMG:1234
        if "EMG:" in line:
            try:
                emg_value = int(line.split(":")[1])

                data.append({
                    "time": datetime.now(),
                    "emg": emg_value
                })
            except:
                pass

except KeyboardInterrupt:
    print("\nStopping and saving data...")

    df = pd.DataFrame(data)
    df.to_csv("emg_data.csv", index=False)

    print("Data saved as emg_data.csv")
