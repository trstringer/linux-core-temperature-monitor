#!/usr/bin/env python3

"""Collect and display relevant hardware temp and load information"""

import csv
from datetime import datetime
import os
import re
import subprocess

def raw_sensor_data():
    """Read the hardware temperature"""

    result = subprocess.run(['sensors'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def parse_fan_speed(sensor_data):
    """Extract the fan speed (in RPM) from sensor data"""

    return int(re.search(r'fan\d:\s+(\d+)\sRPM', sensor_data).group(1))

def parse_core_temps(sensor_data):
    """Extract core temps from sensor data"""

    return {
        i.group(1).replace(' ', '').lower():float(i.group(2))
        for i in re.finditer(r'(Core \d):\s+ \+(\d+\.\d)', sensor_data)
    }

def system_load_past_minute():
    """Retrieve the system load for the past minute"""

    with open('/proc/loadavg') as proc_load_file:
        line = proc_load_file.readline()

    return re.search(r'^\d+\.\d+', line).group(0)

def systemd_cpu_throttle_log():
    """Retrieve any cpu throttling messages in the systemd journal"""

    result = subprocess.run(['journalctl', '--since', '-60s'], stdout=subprocess.PIPE)
    journalctl_output = result.stdout.decode('utf-8')

    return [
        entry for entry in journalctl_output.split('\n')
        if entry != '' and
        'Core temperature above threshold, cpu clock throttled' in entry
    ]

def write_to_csv(data):
    """Write the passed data to a CSV file"""

    with open(os.path.join(os.path.expanduser('~'), 'core_temp.csv'), 'a', newline='') as csv_file:
        fieldnames = ['date_time', 'fan_speed', 'core0_temp', 'core1_temp', 'system_load', 'throttle_logs']
        writer = csv.DictWriter(csv_file, fieldnames)
        writer.writerow(data)

def main():
    """Main script execution"""

    rsd = raw_sensor_data()
    core_temps = parse_core_temps(rsd)
    system_load = system_load_past_minute()
    throttle_logs = ' :::: '.join(systemd_cpu_throttle_log())

    total_output = dict(
        date_time=str(datetime.now()),
        fan_speed=parse_fan_speed(rsd),
        core0_temp=core_temps['core0'],
        core1_temp=core_temps['core1'],
        system_load=system_load,
        throttle_logs=throttle_logs
    )

    print(total_output)

    write_to_csv(total_output)

    if throttle_logs:
        subprocess.run([
            'notify-send',
            'CPU Throttled',
            'core0temp: {}, core1temp: {}, load: {}'.format(
                core_temps['core0'],
                core_temps['core1'],
                system_load
            )
        ])


if __name__ == '__main__':
    main()
