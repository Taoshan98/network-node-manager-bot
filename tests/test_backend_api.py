import pytest
import os
from starlette.testclient import TestClient
from backend.app import app
from backend.storage import Storage, storage


@pytest.fixture(autouse=True)
def reset_storage(tmp_path):
    temp_file = str(tmp_path / "test_nodes.json")
    storage.persistence_file = temp_file
    storage.nodes.clear()
    storage.logs.clear()
    storage._load()
    yield
    if os.path.exists(temp_file):
        os.remove(temp_file)


def test_root_and_health():
    client = TestClient(app)
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"

    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}


def test_get_nodes():
    client = TestClient(app)
    res = client.get("/api/nodes")
    assert res.status_code == 200
    nodes = res.json()
    assert len(nodes) >= 2
    assert nodes[0]["NODE_ID"] == 1
    assert nodes[1]["NODE_ID"] == 2


def test_get_single_node():
    client = TestClient(app)
    res = client.get("/api/nodes/1")
    assert res.status_code == 200
    node = res.json()
    assert node["NODE_ID"] == 1

    res = client.get("/api/nodes/999")
    assert res.status_code == 404


def test_create_and_update_node():
    client = TestClient(app)
    new_node = {
        "NODE_ID": 3,
        "NODE_LAN_IP": "192.168.1.52",
        "NODE_MAC_ADDRESS": "aa:bb:cc:dd:ee:ff",
        "CHECK": "TRUE",
        "WOL": "TRUE",
    }
    res = client.post("/api/nodes", json=new_node)
    assert res.status_code == 200
    created = res.json()
    assert created["NODE_ID"] == 3
    assert created["NODE_LAN_IP"] == "192.168.1.52"

    # Update node
    res = client.put("/api/nodes/3", json={"NODE_LAN_IP": "192.168.1.99"})
    assert res.status_code == 200
    assert res.json()["NODE_LAN_IP"] == "192.168.1.99"


def test_heartbeat_and_logs():
    client = TestClient(app)
    heartbeat_payload = {
        "timestamp": "2026-11-04 12:00:00",
        "wan_ip": "1.2.3.4",
        "battery_status": "Percentage: 85 | Plugged: True",
    }
    res = client.post("/api/nodes/1/heartbeat", json=heartbeat_payload)
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    updated_node = res.json()["node"]
    assert updated_node["TS_LAST_NODE_WRITE"] == "2026-11-04 12:00:00"
    assert updated_node["NODE_WAN_IP"] == "1.2.3.4"
    assert updated_node["BATTERY_STATUS"] == "Percentage: 85 | Plugged: True"
    assert updated_node["STATUS"] == "online"

    # Check logs
    res = client.get("/api/nodes/1/logs")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) == 1
    assert logs[0]["TS"] == "2026-11-04 12:00:00"
    assert logs[0]["WAN_IP"] == "1.2.3.4"


def test_ping_update():
    client = TestClient(app)
    ping_payload = {
        "ping_ts": "2026-11-04 12:05:00",
        "ping_result": "success",
        "last_ping_by": "NODE_1",
        "status": "online",
    }
    res = client.post("/api/nodes/2/ping", json=ping_payload)
    assert res.status_code == 200
    node = res.json()["node"]
    assert node["TS_LAST_PING"] == "2026-11-04 12:05:00"
    assert node["LAST_PING_RESULT"] == "success"
    assert node["LAST_PING_BY"] == "NODE_1"
    assert node["STATUS"] == "online"


def test_check_enable_disable():
    client = TestClient(app)
    # Disable check
    res = client.post("/api/nodes/1/check", json={"check": "FALSE"})
    assert res.status_code == 200
    assert res.json()["node"]["CHECK"] == "FALSE"

    # Enable check with boolean
    res = client.post("/api/nodes/1/check", json={"check": True})
    assert res.status_code == 200
    assert res.json()["node"]["CHECK"] == "TRUE"


def test_delete_node():
    client = TestClient(app)
    res = client.delete("/api/nodes/1")
    assert res.status_code == 200
    assert res.json()["status"] == "deleted"

    res = client.get("/api/nodes/1")
    assert res.status_code == 404


def test_api_key_auth(monkeypatch):
    monkeypatch.setenv("BACKEND_API_KEY", "secret-test-key")
    client = TestClient(app)

    # Without key -> 401
    res = client.get("/api/nodes")
    assert res.status_code == 401

    # With invalid key -> 401
    res = client.get("/api/nodes", headers={"X-API-Key": "wrong-key"})
    assert res.status_code == 401

    # With valid key in header -> 200
    res = client.get("/api/nodes", headers={"X-API-Key": "secret-test-key"})
    assert res.status_code == 200

    # With valid Bearer token -> 200
    res = client.get("/api/nodes", headers={"Authorization": "Bearer secret-test-key"})
    assert res.status_code == 200
