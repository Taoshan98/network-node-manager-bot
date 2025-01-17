import json
import subprocess
import psutil


class Helpers:
    def __init__(self, settings):
        self.settings = settings

    def write_log(self, file, message):
        f = open(f"{file}.log", "a+")
        f.write(f"{message}\n")
        f.close()

    def get_battery_status(self):
        if self.settings.NODE_HAS_BATTERY != 1:
            return 'No Battery', None

        if self.settings.NODE_TYPE == 'ANDROID':
            battery = subprocess.run(["termux-battery-status"], capture_output=True, text=True)
            battery = json.loads(battery.stdout)
            battery_status = (
                f"Percentage: {battery['percentage']} | "
                f"Plugged: {battery['plugged']}"
            )

            return battery_status, battery

        if self.settings.NODE_TYPE == 'LINUX':
            battery = psutil.sensors_battery()
            battery_status = (
                f"Percentage: {battery.percent} | "
                f"Plugged: {battery.power_plugged}"
            )

            return battery_status, {'percentage': battery.percent, 'plugged': battery.power_plugged}
