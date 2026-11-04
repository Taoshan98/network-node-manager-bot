import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional, Any


class BackendController:
    def __init__(self, settings, helpers=None):
        self.settings = settings
        self.helpers = helpers
        self.base_url = (getattr(settings, "BACKEND_URL", None) or "").rstrip("/")
        self.api_key = getattr(settings, "BACKEND_API_KEY", None)

    def _request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        timeout: int = 15,
    ) -> Optional[Any]:
        url = f"{self.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"NNM-Bot-Node/{getattr(self.settings, 'NODE_ID', 'unknown')}",
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode("utf-8")
                if content:
                    return json.loads(content)
                return {}
        except urllib.error.HTTPError as e:
            error_msg = f"BackendController HTTP {e.code} for {method} {url}: {e.read().decode('utf-8', errors='ignore')}"
            if self.helpers:
                self.helpers.write_log("error", error_msg)
            return None
        except Exception as e:
            error_msg = f"BackendController connection error for {method} {url}: {type(e).__name__} – {e}"
            if self.helpers:
                self.helpers.write_log("error", error_msg)
            return None

    def get_nodes(self) -> List[Dict[str, Any]]:
        result = self._request("GET", "/api/nodes")
        if isinstance(result, list):
            return result
        return []

    def read_main_data(self) -> List[Dict[str, Any]]:
        """Backwards compatibility alias for get_nodes."""
        return self.get_nodes()

    def save_node_heartbeat(
        self,
        node_id: int,
        timestamp: str,
        wan_ip: str,
        battery_status: str,
    ) -> Optional[Dict[str, Any]]:
        payload = {
            "timestamp": timestamp,
            "wan_ip": wan_ip,
            "battery_status": battery_status,
        }
        return self._request("POST", f"/api/nodes/{int(node_id)}/heartbeat", payload)

    def write_node_data(self, data) -> None:
        """Backwards compatibility for when a DataFrame or dict is passed."""
        try:
            if hasattr(data, "to_dict"):
                records = data.to_dict(orient="records")
                if records:
                    rec = records[0]
                    self.save_node_heartbeat(
                        self.settings.NODE_ID,
                        rec.get("TS", ""),
                        rec.get("WAN_IP", ""),
                        rec.get("BATTERY_STATUS", ""),
                    )
            elif isinstance(data, dict):
                self.save_node_heartbeat(
                    self.settings.NODE_ID,
                    data.get("TS", ""),
                    data.get("WAN_IP", ""),
                    data.get("BATTERY_STATUS", ""),
                )
        except Exception as e:
            if self.helpers:
                self.helpers.write_log("error", f"BackendController write_node_data error: {e}")

    def update_node_ping(
        self,
        node_id: int,
        ping_ts: str,
        ping_result: str,
        last_ping_by: str,
        status: str,
    ) -> Optional[Dict[str, Any]]:
        payload = {
            "ping_ts": ping_ts,
            "ping_result": ping_result,
            "last_ping_by": last_ping_by,
            "status": status,
        }
        return self._request("POST", f"/api/nodes/{int(node_id)}/ping", payload)

    def update_node_check(self, node_id: int, check: Any) -> Optional[Dict[str, Any]]:
        val = "TRUE" if str(check).upper() in ("TRUE", "1") else "FALSE"
        payload = {"check": val}
        return self._request("POST", f"/api/nodes/{int(node_id)}/check", payload)

    def update_main_data(self, row: int, cell: int, value: Any) -> None:
        """Backwards compatibility for spreadsheet cell updates."""
        node_id = row - 1
        if cell == 11:
            self.update_node_check(node_id, value)
        elif cell in (6, 7, 8, 9):
            # Map cell to ping parameters if called individually
            node = next((n for n in self.get_nodes() if n.get("NODE_ID") == node_id), {})
            ping_ts = value if cell == 6 else node.get("TS_LAST_PING", "")
            ping_result = value if cell == 7 else node.get("LAST_PING_RESULT", "")
            last_ping_by = value if cell == 8 else node.get("LAST_PING_BY", "")
            status = value if cell == 9 else node.get("STATUS", "")
            self.update_node_ping(node_id, ping_ts, ping_result, last_ping_by, status)
