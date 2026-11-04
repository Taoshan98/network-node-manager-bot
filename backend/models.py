from typing import Optional, Any, List
from pydantic import BaseModel, Field


class Node(BaseModel):
    NODE_ID: int
    NODE_LAN_IP: str = ""
    NODE_WAN_IP: Optional[str] = ""
    NODE_MAC_ADDRESS: Optional[str] = ""
    TS_LAST_NODE_WRITE: Optional[str] = ""
    TS_LAST_PING: Optional[str] = ""
    LAST_PING_RESULT: Optional[str] = ""
    LAST_PING_BY: Optional[str] = ""
    STATUS: Optional[str] = "offline"
    BATTERY_STATUS: Optional[str] = ""
    CHECK: str = "TRUE"
    WOL: str = "FALSE"


class HeartbeatRequest(BaseModel):
    timestamp: Optional[str] = None
    wan_ip: Optional[str] = None
    battery_status: Optional[str] = None


class PingUpdateRequest(BaseModel):
    ping_ts: Optional[str] = None
    ping_result: Optional[str] = None
    last_ping_by: Optional[str] = None
    status: Optional[str] = None


class CheckUpdateRequest(BaseModel):
    check: Any


class NodeCreateOrUpdateRequest(BaseModel):
    NODE_ID: Optional[int] = None
    NODE_LAN_IP: Optional[str] = None
    NODE_WAN_IP: Optional[str] = None
    NODE_MAC_ADDRESS: Optional[str] = None
    TS_LAST_NODE_WRITE: Optional[str] = None
    TS_LAST_PING: Optional[str] = None
    LAST_PING_RESULT: Optional[str] = None
    LAST_PING_BY: Optional[str] = None
    STATUS: Optional[str] = None
    BATTERY_STATUS: Optional[str] = None
    CHECK: Optional[Any] = None
    WOL: Optional[Any] = None


class HeartbeatLog(BaseModel):
    TS: str
    WAN_IP: str
    BATTERY_STATUS: str
