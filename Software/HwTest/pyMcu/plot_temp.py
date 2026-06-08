import re
import argparse
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

# Set up argument parser
parser = argparse.ArgumentParser(description='Process a log file to plot temperature over time.')
parser.add_argument('log_file_path', type=str, help='Path to the log file')
args = parser.parse_args()

# Read the log file
with open(args.log_file_path, "r") as f:
    log_text = f.read()

# Pattern to extract timestamped blocks
block_pattern = re.compile(r"(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})(.*?)\n(?=\d{2}\.\d{2}\.\d{4}|\Z)", re.DOTALL)
blocks = block_pattern.findall(log_text)

# Dictionary to hold temperature data per sensor
sensor_data = defaultdict(list)

# Parse blocks
for timestamp_str, block in blocks:
    timestamp = datetime.strptime(timestamp_str, "%d.%m.%Y %H:%M:%S")
    for line in block.strip().splitlines():
        match = re.match(r"(.*?):\s*([\d.]+)\s*degC", line)
        if match:
            sensor_name = match.group(1).strip()
            temperature = float(match.group(2))
            sensor_data[sensor_name].append((timestamp, temperature))

# Plotting
plt.figure(figsize=(15, 8))
for sensor, readings in sensor_data.items():
    times, temps = zip(*readings)
    plt.plot(times, temps, label=sensor)

plt.title("Temperature Over Time for All Sensors")
plt.xlabel("Time")
plt.ylabel("Temperature (°C)")
plt.legend(loc="upper left", bbox_to_anchor=(1, 1), fontsize="small")
plt.grid(True)
plt.tight_layout()
plt.xticks(rotation=45)
plt.show()

