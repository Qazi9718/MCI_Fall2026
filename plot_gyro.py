
import serial
import matplotlib.pyplot as plt
from collections import deque

ser = serial.Serial("COM3", 115200, timeout=1)

x_data = deque(maxlen=200)
y_data = deque(maxlen=200)
z_data = deque(maxlen=200)
time_data = deque(maxlen=200)

plt.ion()
fig, ax = plt.subplots()

line_x, = ax.plot([], [], label="X")
line_y, = ax.plot([], [], label="Y")
line_z, = ax.plot([], [], label="Z")

ax.set_xlabel("Time (seconds)")
ax.set_ylabel("Angular velocity (dps)")
ax.set_title("Live Gyroscope Readings")
ax.legend()
ax.grid(True)

start = None

try:
    while True:
        text = ser.readline().decode("utf-8", errors="ignore").strip()

        if not text:
            continue

        values = text.split(",")

        if len(values) != 4:
            continue

        try:
            temp = int(values[0])
            x = int(values[1]) / 100.0
            y = int(values[2]) / 100.0
            z = int(values[3]) / 100.0
        except ValueError:
            continue

        if start is None:
            start = __import__("time").time()

        t = __import__("time").time() - start

        time_data.append(t)
        x_data.append(x)
        y_data.append(y)
        z_data.append(z)

        line_x.set_data(time_data, x_data)
        line_y.set_data(time_data, y_data)
        line_z.set_data(time_data, z_data)

        ax.relim()
        ax.autoscale_view()
        plt.pause(0.01)

except KeyboardInterrupt:
    pass

finally:
    ser.close()
    plt.close()
