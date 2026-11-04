import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone

DEFAULT_NODES: List[Dict[str, Any]] = [
    {
        "NODE_ID": 1,
        "NODE_LAN_IP": "192.168.1.50",
        "NODE_WAN_IP": "",
        "NODE_MAC_ADDRESS": "10:62:e5:18:f4:fa",
        "TS_LAST_NODE_WRITE": "",
        "TS_LAST_PING": "",
        "LAST_PING_RESULT": "",
        "LAST_PING_BY": "",
        "STATUS": "offline",
        "BATTERY_STATUS": "No Battery",
        "CHECK": "TRUE",
        "WOL": "TRUE",
    },
    {
        "NODE_ID": 2,
        "NODE_LAN_IP": "192.168.1.51",
        "NODE_WAN_IP": "",
        "NODE_MAC_ADDRESS": "5c:17:cf:92:bf:44",
        "TS_LAST_NODE_WRITE": "",
        "TS_LAST_PING": "",
        "LAST_PING_RESULT": "",
        "LAST_PING_BY": "",
        "STATUS": "offline",
        "BATTERY_STATUS": "",
        "CHECK": "TRUE",
        "WOL": "FALSE",
    },
]


class Storage:
    def __init__(self, persistence_file: Optional[str] = None):
        self.persistence_file = persistence_file or os.getenv(
            "NODES_FILE_PATH", "/tmp/nnm_nodes.json"
        )
        self.nodes: Dict[int, Dict[str, Any]] = {}
        self.logs: Dict[int, List[Dict[str, str]]] = {}
        self._load()

    def _normalize_bool_str(self, val: Any) -> str:
        if isinstance(val, bool):
            return "TRUE" if val else "FALSE"
        if isinstance(val, (int, float)):
            return "TRUE" if val == 1 else "FALSE"
        if isinstance(val, str):
            return "TRUE" if val.strip().upper() in ("TRUE", "1", "YES", "T") else "FALSE"
        return "FALSE"

    def _load(self):
        # 1. Try loading from file
        if self.persistence_file and os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    raw_nodes = data.get("nodes", [])
                    for node in raw_nodes:
                        node_id = int(node["NODE_ID"])
                        self.nodes[node_id] = node
                    self.logs = {int(k): v for k, v in data.get("logs", {}).items()}
                    return
            except Exception:
                pass

        # 2. Try loading from INITIAL_NODES environment variable
        initial_nodes_env = os.getenv("INITIAL_NODES")
        if initial_nodes_env:
            try:
                parsed = json.loads(initial_nodes_env)
                if isinstance(parsed, list):
                    for node in parsed:
                        node_id = int(node["NODE_ID"])
                        self.nodes[node_id] = node
                    return
            except Exception:
                pass

        # 3. Fallback to DEFAULT_NODES
        for node in DEFAULT_NODES:
            node_id = int(node["NODE_ID"])
            self.nodes[node_id] = dict(node)

    def _save(self):
        if not self.persistence_file:
            return
        try:
            parent_dir = os.path.dirname(self.persistence_file)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            with open(self.persistence_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "nodes": list(self.nodes.values()),
                        "logs": self.logs,
                    },
                    f,
                    indent=2,
                )
        except Exception:
            pass

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        # Sort by NODE_ID
        return sorted(list(self.nodes.values()), key=lambda x: x.get("NODE_ID", 0))

    def get_node(self, node_id: int) -> Optional[Dict[str, Any]]:
        return self.nodes.get(int(node_id))

    def upsert_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        node_id = int(node_data["NODE_ID"])
        existing = self.nodes.get(node_id, {})
        updated = {**existing, **node_data}
        updated["NODE_ID"] = node_id
        if "CHECK" in updated:
            updated["CHECK"] = self._normalize_bool_str(updated["CHECK"])
        if "WOL" in updated:
            updated["WOL"] = self._normalize_bool_str(updated["WOL"])
        self.nodes[node_id] = updated
        self._save()
        return updated

    def delete_node(self, node_id: int) -> bool:
        node_id = int(node_id)
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.logs.pop(node_id, None)
            self._save()
            return True
        return False

    def update_heartbeat(
        self,
        node_id: int,
        timestamp: Optional[str] = None,
        wan_ip: Optional[str] = None,
        battery_status: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        node_id = int(node_id)
        node = self.nodes.get(node_id)
        if not node:
            # Auto-create node stub if it doesn't exist
            node = {
                "NODE_ID": node_id,
                "NODE_LAN_IP": "",
                "NODE_WAN_IP": "",
                "NODE_MAC_ADDRESS": "",
                "TS_LAST_NODE_WRITE": "",
                "TS_LAST_PING": "",
                "LAST_PING_RESULT": "",
                "LAST_PING_BY": "",
                "STATUS": "online",
                "BATTERY_STATUS": "",
                "CHECK": "TRUE",
                "WOL": "FALSE",
            }
            self.nodes[node_id] = node

        ts = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        node["TS_LAST_NODE_WRITE"] = ts
        if wan_ip is not None:
            node["NODE_WAN_IP"] = wan_ip
        if battery_status is not None:
            node["BATTERY_STATUS"] = battery_status
        node["STATUS"] = "online"

        # Log heartbeat entry
        if node_id not in self.logs:
            self.logs[node_id] = []
        self.logs[node_id].append(
            {
                "TS": ts,
                "WAN_IP": wan_ip or node.get("NODE_WAN_IP", ""),
                "BATTERY_STATUS": battery_status or node.get("BATTERY_STATUS", ""),
            }
        )
        if len(self.logs[node_id]) > 500:
            self.logs[node_id] = self.logs[node_id][-500:]

        self._save()
        return node

    def update_ping(
        self,
        node_id: int,
        ping_ts: Optional[str] = None,
        ping_result: Optional[str] = None,
        last_ping_by: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        node_id = int(node_id)
        node = self.nodes.get(node_id)
        if not node:
            return None

        if ping_ts is not None:
            node["TS_LAST_PING"] = ping_ts
        if ping_result is not None:
            node["LAST_PING_RESULT"] = ping_result
        if last_ping_by is not None:
            node["LAST_PING_BY"] = last_ping_by
        if status is not None:
            node["STATUS"] = status

        self._save()
        return node

    def update_check(self, node_id: int, check: Any) -> Optional[Dict[str, Any]]:
        node_id = int(node_id)
        node = self.nodes.get(node_id)
        if not node:
            return None

        node["CHECK"] = self._normalize_bool_str(check)
        self._save()
        return node

    def get_logs(self, node_id: int, limit: int = 50) -> List[Dict[str, str]]:
        node_id = int(node_id)
        node_logs = self.logs.get(node_id, [])
        return node_logs[-limit:]


# Global storage instance
storage = Storage()
