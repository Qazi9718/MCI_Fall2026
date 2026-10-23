import serial
import time
import matplotlib.pyplot as plt

PORT = 'COM3'
BAUD = 115200

# Attempt port connection with auto-retry if port is briefly busy
print(f"Connecting to {PORT}...")
sinWaveData = None
for _ in range(5):
    try:
        sinWaveData = serial.Serial(PORT, BAUD, timeout=1)
        break
    except serial.SerialException:
        print("Port busy, retrying in 1 second... (Ensure VS Code Serial Monitor is STOPPED)")
        time.sleep(1)

if sinWaveData is None or not sinWaveData.is_open:
    print(f"Error: Could not open {PORT}. Unplug and replug the STM32 USB cable, then re-run.")
    exit(1)

print(f"Connected to {PORT}. Initializing plot window...")

# Setup interactive plotting
plt.ion()
fig, ax = plt.subplots()
raw_line_plot, = ax.plot([], [], 'r-', label='Raw ADC')
filt_line_plot, = ax.plot([], [], 'b-', linewidth=2, label='Filtered (Moving Avg)')

ax.set_title('Live ADC & Filtered Data (CMSIS DSP)')
ax.set_xlabel('Sample Count')
ax.set_ylabel('ADC Counts (0 - 4095)')
ax.set_ylim(0, 4200)
ax.set_xlim(0, 200)
ax.grid(True)
ax.legend(loc='upper left')

adcValues = []
filteredValues = []
x_indices = []
cnt = 0

try:
    while True:
        raw_bytes = sinWaveData.readline()
        if not raw_bytes:
            continue

        line = raw_bytes.decode('utf-8', errors='ignore').strip()

        if "Raw:" in line and "Filtered:" in line:
            try:
                parts = line.split(',')
                raw_val = float(parts[0].split(':')[1].strip())
                filt_val = float(parts[1].split(':')[1].strip())

                adcValues.append(raw_val)
                filteredValues.append(filt_val)
                x_indices.append(cnt)
                cnt += 1

                # Keep a rolling window of 200 data points
                if len(adcValues) > 200:
                    adcValues.pop(0)
                    filteredValues.pop(0)
                    x_indices.pop(0)

                # Update line data dynamically (high performance, no GUI freezes)
                if cnt % 3 == 0:  # refresh render every 3 samples
                    raw_line_plot.set_data(range(len(adcValues)), adcValues)
                    filt_line_plot.set_data(range(len(filteredValues)), filteredValues)
                    ax.set_xlim(0, len(adcValues))
                    fig.canvas.draw_idle()
                    plt.pause(0.001)

            except (ValueError, IndexError):
                continue

except KeyboardInterrupt:
    print("\nExiting cleanly...")
finally:
    if sinWaveData and sinWaveData.is_open:
        sinWaveData.close()
    plt.close('all')
    print("Port closed successfully.")