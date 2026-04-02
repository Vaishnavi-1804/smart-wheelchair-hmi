import serial
import matplotlib.pyplot as plt
from collections import deque

# Serial setup (change COM port)
ser = serial.Serial('COM3', 115200)

# Store last 100 values
data = deque([0]*100, maxlen=100)

plt.ion()  # interactive mode
fig, ax = plt.subplots()
line, = ax.plot(data)

ax.set_title("Live EMG Signal")
ax.set_xlabel("Samples")
ax.set_ylabel("EMG Value")

print("Live plotting started... Press Ctrl+C to stop")

try:
    while True:
        line_data = ser.readline().decode().strip()

        if "EMG:" in line_data:
            try:
                value = int(line_data.split(":")[1])
                data.append(value)

                line.set_ydata(data)
                line.set_xdata(range(len(data)))

                ax.relim()
                ax.autoscale_view()

                plt.draw()
                plt.pause(0.01)

            except:
                pass

except KeyboardInterrupt:
    print("Stopped")
