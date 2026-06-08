#!/usr/bin/env python3

import argparse
from asyncio import sleep
import csv
import re
import subprocess
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time

#SERIAL_DEVICE = "/dev/ttyUL1"
VERBOSITY = "0"

script_dir = Path(__file__).resolve().parent

MARKER = "Resp. from command:"

parser = argparse.ArgumentParser(description="Monitor MCU power and temperature.")
parser.add_argument(
    "-d", "--device",
    default="/dev/ttyUL1",
    help="Serial device to use (default: /dev/ttyUL1)",
)
parser.add_argument(
    "-l", "--local-pymcu",
    action="store_true",
    help="Use local pyMcuCm.py instead of system-wide (default: False)"
)
parser.add_argument("--no_service", action="store_true", help="Run without mcu_client (default: False)")

parser.add_argument(
    "-o", "--output",
    default="endurance_{}".format(datetime.now().strftime("%Y%m%d_%H%M%S")),
    help="Output folder (default: endurance_<date>)",
)
args = parser.parse_args()
SERIAL_DEVICE = args.device

output_dir = Path(args.output)
output_dir.mkdir(parents=True, exist_ok=True)

CSV_FILE = output_dir / ("monitor_log_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv")
PLOT_FILE = output_dir / ("monitor_log_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".pdf")

TEMP_RE  = re.compile(r'^(.+?)\s*:\s*([\d.]+)\s*degC$')
VOLT_RE  = re.compile(r'^(.+?)\s*:\s*([\d.]+)\s*V,\s*([\d.]+)\s*A$')
POWER_RE = re.compile(r'^Total power\s*:\s*([\d.]+)\s*W$')
FF_RE    = re.compile(r'^(FF\d+\s+(?:TX|RX))\s*:\s*([\d.]+)\s*degC\s+([\d.]+)\s*V$')

def run_mcu(command):
    if args.local_pymcu:
        pyMcu_path = script_dir / "pyMcuCm.py"
    else:        
        pyMcu_path = "pyMcuCm.py"

    if args.no_service:
        mcu_client_cmd = ""
    else:
        mcu_client_cmd = "mcu_client"

    result = subprocess.run(
        [str(mcu_client_cmd), str(pyMcu_path), "-d", SERIAL_DEVICE, "-v", VERBOSITY, "-c", command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=script_dir,
    )
    return result.stdout.decode("utf-8")

def get_responses(output):
    lines = []
    for line in output.splitlines():
        if MARKER in line:
        # lines.append(line.strip())
            lines.append(line.split(MARKER, 1)[1].strip())
        else:
            lines.append(line.strip())
    return lines

def parse_temps(lines):
    data = {}
    for line in lines:
        m = TEMP_RE.match(line)
        if m:
            data[m.group(1).strip() + " [degC]"] = float(m.group(2))
    return data

def parse_ff_status(lines):
    data = {}
    for line in lines:
        m = FF_RE.match(line)
        if m:
            name = m.group(1).strip()
            data["{} [degC]".format(name)] = float(m.group(2))
            data["{} [V]".format(name)]    = float(m.group(3))
    return data

def parse_power(lines):
    data = {}
    section = ""
    for line in lines:
        if not line:
            continue
        if ":" not in line:
            section = line.strip()
            continue
        m = VOLT_RE.match(line)
        if m:
            name = m.group(1).strip()
            data["{} - {} [V]".format(section, name)] = float(m.group(2))
            data["{} - {} [A]".format(section, name)] = float(m.group(3))
            continue
        m = POWER_RE.match(line)
        if m:
            data["{} - Total power [W]".format(section)] = float(m.group(1))
    return data

all_rows = []
headers = []
csv_file = None

def write_csv():
    global csv_file
    if csv_file:
        csv_file.close()
    csv_file = open(str(CSV_FILE), "w")
    writer = csv.DictWriter(csv_file, fieldnames=headers, restval="")
    writer.writeheader()
    for r in all_rows:
        writer.writerow(r)
    csv_file.flush()

try:
    while True:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        print(timestamp)

        temp_lines  = get_responses(run_mcu("mon_temp"))
        time.sleep(1)
        power_lines = get_responses(run_mcu("power_detail"))
        time.sleep(1)
        ff_lines    = get_responses(run_mcu("ff_status"))
        time.sleep(1)
        for line in temp_lines + power_lines + ff_lines:
            print(line)
        print()

        row = {"timestamp": timestamp}
        row.update(parse_temps(temp_lines))
        row.update(parse_power(power_lines))
        row.update(parse_ff_status(ff_lines))
        all_rows.append(row)

        new_fields = [k for k in row if k not in headers]
        if new_fields:
            headers.extend(new_fields)
            write_csv()
        else:
            writer = csv.DictWriter(csv_file, fieldnames=headers, restval="")
            writer.writerow(row)
            csv_file.flush()

except KeyboardInterrupt:
    print("\nStopped.")
    if len(all_rows) >= 2:
        times = [datetime.strptime(r["timestamp"], "%d.%m.%Y %H:%M:%S") for r in all_rows]
        temp_cols = [h for h in headers if h.endswith("[degC]") and not re.match(r'^FF\d+', h)]
        ff_temp_cols = [h for h in headers if re.match(r'^FF\d+', h) and h.endswith("[degC]")]

        fig, (ax_temp, ax_ff, ax_volt) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
        fig.suptitle("Monitor log - {}".format(all_rows[0]["timestamp"]))

        for col in temp_cols:
            values = [r.get(col, None) for r in all_rows]
            ax_temp.plot(times, values, marker=".", markersize=3, label=col.replace(" [degC]", ""))
        if ff_temp_cols:
            max_ff = [
                max((r.get(col) for col in ff_temp_cols if r.get(col) is not None), default=None)
                for r in all_rows
            ]
            ax_temp.plot(times, max_ff, marker=".", markersize=3, linestyle="--", linewidth=2, label="FF max")
        ax_temp.set_ylabel("Temperature [degC]")
        ax_temp.legend(loc="upper left", fontsize=7, ncol=2)
        ax_temp.grid(True)

        for col in ff_temp_cols:
            values = [r.get(col, None) for r in all_rows]
            ax_ff.plot(times, values, marker=".", markersize=2, label=col.replace(" [degC]", ""))
        ax_ff.set_ylabel("FF Temperature [degC]")
        ax_ff.legend(loc="upper left", fontsize=6, ncol=4)
        ax_ff.grid(True)

        power_cols = [h for h in headers if h.endswith("Total power [W]")]
        for col in power_cols:
            values = [r.get(col, None) for r in all_rows]
            ax_volt.plot(times, values, marker=".", markersize=3, label=col.replace(" - Total power [W]", ""))
        total_power = [
            sum(r.get(col, 0) or 0 for col in power_cols)
            for r in all_rows
        ]
        ax_volt.plot(times, total_power, marker=".", markersize=3, linestyle="--", linewidth=2, label="Total")
        ax_volt.set_ylabel("Power [W]")
        ax_volt.set_xlabel("Time")
        ax_volt.legend(loc="upper left", fontsize=7, ncol=2)
        ax_volt.grid(True)

        ax_volt.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        fig.autofmt_xdate()
        plt.tight_layout()
        plt.savefig(PLOT_FILE)
    else:
        print("Not enough data to plot.")
finally:
    if csv_file:
        csv_file.close()
        print("CSV saved to: {}".format(CSV_FILE))
