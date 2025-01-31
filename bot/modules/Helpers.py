import json
import subprocess
import psutil
import time


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

    def ping(self, host):
        count_param = '-c'
        if self.settings.NODE_TYPE == 'WINDOWS':
            count_param = '-n 1'

        return subprocess.run(
            ["ping", count_param, "1", host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def wait_for_internet(self, timeout=30):
        ping = self.ping("8.8.8.8")

        while ping.returncode > 0:
            self.write_log('error', "Internet connection not available!")
            time.sleep(timeout)
            ping = self.ping("8.8.8.8")
