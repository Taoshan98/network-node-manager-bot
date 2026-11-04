from typing import List, Dict, Any, Optional
from bot.controllers.BackendController import BackendController
from bot.controllers.SpreadSheetController import SpreadSheetController


class CombinedStorageController:
    """
    Coordinates operations across both a serverless backend and Google Spreadsheets.
    Enables dual-write operations and graceful fallback for high reliability.
    """

    def __init__(self, settings, helpers=None):
        self.settings = settings
        self.helpers = helpers
        self.backend = BackendController(settings, helpers)
        self.spreadsheet = None

        try:
            self.spreadsheet = SpreadSheetController(settings)
        except Exception as e:
            if self.helpers:
                self.helpers.write_log(
                    "error",
                    f"CombinedStorageController: Could not initialize SpreadSheetController: {e}",
                )

    def get_nodes(self) -> List[Dict[str, Any]]:
        nodes = self.backend.get_nodes()
        if nodes:
            return nodes
        if self.spreadsheet:
            try:
                return self.spreadsheet.get_nodes()
            except Exception as e:
                if self.helpers:
                    self.helpers.write_log("error", f"CombinedStorageController get_nodes spreadsheet error: {e}")
        return []

    def read_main_data(self) -> List[Dict[str, Any]]:
        return self.get_nodes()

    def save_node_heartbeat(
        self,
        node_id: int,
        timestamp: str,
        wan_ip: str,
        battery_status: str,
    ) -> None:
        self.backend.save_node_heartbeat(node_id, timestamp, wan_ip, battery_status)
        if self.spreadsheet:
            try:
                self.spreadsheet.save_node_heartbeat(node_id, timestamp, wan_ip, battery_status)
            except Exception as e:
                if self.helpers:
                    self.helpers.write_log("error", f"CombinedStorageController spreadsheet heartbeat error: {e}")

    def write_node_data(self, data) -> None:
        self.backend.write_node_data(data)
        if self.spreadsheet:
            try:
                self.spreadsheet.write_node_data(data)
            except Exception as e:
                if self.helpers:
                    self.helpers.write_log("error", f"CombinedStorageController spreadsheet write_node_data error: {e}")

    def update_node_ping(
        self,
        node_id: int,
        ping_ts: str,
        ping_result: str,
        last_ping_by: str,
        status: str,
    ) -> None:
        self.backend.update_node_ping(node_id, ping_ts, ping_result, last_ping_by, status)
        if self.spreadsheet:
            try:
                self.spreadsheet.update_node_ping(node_id, ping_ts, ping_result, last_ping_by, status)
            except Exception as e:
                if self.helpers:
                    self.helpers.write_log("error", f"CombinedStorageController spreadsheet update_ping error: {e}")

    def update_node_check(self, node_id: int, check: Any) -> None:
        self.backend.update_node_check(node_id, check)
        if self.spreadsheet:
            try:
                self.spreadsheet.update_node_check(node_id, check)
            except Exception as e:
                if self.helpers:
                    self.helpers.write_log("error", f"CombinedStorageController spreadsheet update_check error: {e}")

    def update_main_data(self, row: int, cell: int, value: Any) -> None:
        self.backend.update_main_data(row, cell, value)
        if self.spreadsheet:
            try:
                self.spreadsheet.update_main_data(row, cell, value)
            except Exception as e:
                if self.helpers:
                    self.helpers.write_log("error", f"CombinedStorageController spreadsheet update_main_data error: {e}")
