import os
import urllib.request
from datetime import datetime, timezone
import pandas as pd
from telegram.constants import ParseMode
from wakeonlan import send_magic_packet


class NodesController:
    def __init__(self, settings, spreadsheet, helpers):
        self.settings = settings
        self.spreadsheet = spreadsheet
        self.helpers = helpers
        self.application = None
        self.node_battery_alerts = [90, 80, 70, 60, 50, 40, 30, 20, 15, 10, 5]
        self.previous_battery_percentage = 100

    async def handle(self, application):
        self.application = application

        battery_status, battery = self.helpers.get_battery_status()

        self._save_node_data(battery_status)

        if self._should_send_battery_alert(battery):
            await self._send_battery_alert(battery)

        nodes = self.spreadsheet.read_main_data()
        await self._process_nodes(nodes)

    def _should_send_battery_alert(self, battery):
        return (
                battery is not None and battery['percentage'] in self.node_battery_alerts
                and battery['percentage'] != self.previous_battery_percentage
        )

    async def _send_battery_alert(self, battery):
        status_message = self._get_battery_status_message(battery['percentage'])
        self.previous_battery_percentage = battery['percentage']

        await self.application.bot.send_message(
            chat_id=self.settings.TELEGRAM_MAIN_GROUP,
            text=status_message,
            parse_mode=ParseMode.HTML
        )

    def _get_battery_status_message(self, percentage):
        if percentage < self.previous_battery_percentage:
            return f"Battery is getting low 😵‍💫\nCurrent {percentage}% 🪫"
        elif percentage > self.previous_battery_percentage:
            return f"Battery is getting up 😊\nCurrent {percentage}% ⚡"
        elif percentage == 100 and self.previous_battery_percentage < 100:
            return f"Battery Full 🤩\nCurrent {percentage}% 🔋"
        return f"Current {percentage}%"

    async def _process_nodes(self, nodes):
        for node in nodes:
            if not self._should_process_node(node):
                continue

            row = node['NODE_ID'] + 1

            node_name = f'NODE_{self.settings.NODE_ID}'
            ping_ts = self._get_current_timestamp()
            ping_result = self._ping_node(node['NODE_LAN_IP'])

            node_status = self._check_node_status(node['TS_LAST_NODE_WRITE'])
            self._update_node_data(row, ping_ts, ping_result, node_name, node_status)

            if node_status == 'offline' and ping_result == 'failed' and node['WOL'] == 'TRUE':
                await self._send_node_alert(node)

    def _should_process_node(self, node):
        return node['NODE_ID'] != self.settings.NODE_ID and node['CHECK'] == 'TRUE'

    def _update_node_data(self, row, ping_ts, ping_result, node_name, node_status):
        self.spreadsheet.update_main_data(row, 6, ping_ts)
        self.spreadsheet.update_main_data(row, 7, ping_result)
        self.spreadsheet.update_main_data(row, 8, node_name)
        self.spreadsheet.update_main_data(row, 9, node_status)

    async def _send_node_alert(self, node):
        await self.application.bot.send_message(
            chat_id=self.settings.TELEGRAM_MAIN_GROUP,
            text=f"the node {node['NODE_ID']} is offline! ❌\nI try to revive him ❤️‍🩹",
            parse_mode=ParseMode.HTML
        )
        send_magic_packet(node['NODE_MAC_ADDRESS'])

    def _check_node_status(self, node_timestamp):
        node_timestamp = datetime.strptime(node_timestamp, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        current_timestamp = datetime.now(timezone.utc)

        difference = (current_timestamp - node_timestamp).total_seconds() / 60

        return 'offline' if difference > 10 else 'online'

    def _save_node_data(self, battery_status):
        ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        timestamp = self._get_current_timestamp()
        node_data = pd.DataFrame({"TS": [timestamp], "WAN_IP": [ip], "BATTERY_STATUS": [battery_status]})
        self.spreadsheet.write_node_data(node_data)

    def _ping_node(self, host):
        ping = self.helpers.ping(host)
        return 'failed' if ping.returncode > 0 else 'success'

    def _get_current_timestamp(self):
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
