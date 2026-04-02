import serial

ser = serial.Serial('COM3', 115200)

print("EMG Control Started...")

# Define thresholds (you will tune these)
LOW_THRESHOLD = 1200
HIGH_THRESHOLD = 2000

try:
    while True:
        line = ser.readline().decode().strip()

        if "EMG:" in line:
            try:
                value = int(line.split(":")[1])
                print("EMG:", value)

                if value < LOW_THRESHOLD:
                    print("Action: STOP")

                elif LOW_THRESHOLD <= value < HIGH_THRESHOLD:
                    print("Action: MOVE FORWARD")

                else:
                    print("Action: FAST / TURN")

            except:
                pass

except KeyboardInterrupt:
    print("Stopped")
