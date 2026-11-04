import pytest
import threading
import time
import uvicorn
from config.Settings import Settings
from bot.controllers.BackendController import BackendController
from bot.controllers.NodesController import NodesController
from bot.controllers.StorageController import get_storage_controller
from bot.controllers.CombinedStorageController import CombinedStorageController
from bot.modules.Helpers import Helpers
from backend.storage import storage


class MockApplication:
    def __init__(self):
        self.bot = MockBot()


class MockBot:
    def __init__(self):
        self.sent_messages = []

    async def send_message(self, chat_id, text, parse_mode=None):
        self.sent_messages.append({"chat_id": chat_id, "text": text, "parse_mode": parse_mode})


class MockContext:
    def __init__(self, args=None):
        self.args = args or []
        self.bot = MockBot()


class MockUpdate:
    def __init__(self):
        self.message = MockMessage()


class MockMessage:
    def __init__(self):
        self.chat_id = 12345
        self.message_thread_id = None
        self.from_user = type("User", (), {"id": 12345})()


@pytest.fixture(scope="module")
def backend_server():
    server_port = 8765
    config = uvicorn.Config("backend.app:app", host="127.0.0.1", port=server_port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for server to start
    start_time = time.time()
    while not server.started and time.time() - start_time < 5:
        time.sleep(0.05)

    yield f"http://127.0.0.1:{server_port}"
    server.should_exit = True


def test_settings_auto_detection(monkeypatch):
    monkeypatch.delenv("BACKEND_URL", raising=False)
    monkeypatch.delenv("SPREADSHEET_URL", raising=False)
    monkeypatch.delenv("DATA_BACKEND", raising=False)

    # Default without any URL -> BACKEND
    s = Settings()
    assert s.DATA_BACKEND == "BACKEND"

    # With BACKEND_URL -> BACKEND
    monkeypatch.setenv("BACKEND_URL", "http://example.com")
    s = Settings()
    assert s.DATA_BACKEND == "BACKEND"

    # With SPREADSHEET_URL -> SPREADSHEET
    monkeypatch.delenv("BACKEND_URL", raising=False)
    monkeypatch.setenv("SPREADSHEET_URL", "https://docs.google.com/spreadsheets/d/123")
    s = Settings()
    assert s.DATA_BACKEND == "SPREADSHEET"

    # With both -> COMBINED
    monkeypatch.setenv("BACKEND_URL", "http://example.com")
    monkeypatch.setenv("SPREADSHEET_URL", "https://docs.google.com/spreadsheets/d/123")
    s = Settings()
    assert s.DATA_BACKEND == "COMBINED"

    # Explicit override
    monkeypatch.setenv("DATA_BACKEND", "BACKEND")
    s = Settings()
    assert s.DATA_BACKEND == "BACKEND"


def test_storage_controller_factory(monkeypatch):
    monkeypatch.setenv("BACKEND_URL", "http://example.com")
    monkeypatch.setenv("DATA_BACKEND", "BACKEND")
    s = Settings()
    controller = get_storage_controller(s)
    assert isinstance(controller, BackendController)


def test_backend_controller_operations(backend_server, monkeypatch):
    monkeypatch.setenv("BACKEND_URL", backend_server)
    monkeypatch.setenv("NODE_ID", "1")
    s = Settings()
    bc = BackendController(s)

    # 1. Get nodes
    nodes = bc.get_nodes()
    assert len(nodes) >= 2
    assert nodes[0]["NODE_ID"] == 1

    # 2. Save heartbeat
    res = bc.save_node_heartbeat(
        node_id=1,
        timestamp="2026-11-04 15:00:00",
        wan_ip="5.6.7.8",
        battery_status="Percentage: 95 | Plugged: True",
    )
    assert res is not None
    assert res["status"] == "ok"

    # 3. Update ping
    res = bc.update_node_ping(
        node_id=2,
        ping_ts="2026-11-04 15:01:00",
        ping_result="success",
        last_ping_by="NODE_1",
        status="online",
    )
    assert res is not None
    assert res["status"] == "ok"

    # 4. Update check
    res = bc.update_node_check(node_id=2, check=False)
    assert res is not None
    assert res["node"]["CHECK"] == "FALSE"

    res = bc.update_node_check(node_id=2, check="TRUE")
    assert res is not None
    assert res["node"]["CHECK"] == "TRUE"

    # 5. Backwards-compatible aliases
    assert len(bc.read_main_data()) >= 2
    bc.update_main_data(row=3, cell=11, value="FALSE")  # row 3 = node 2
    updated_nodes = bc.get_nodes()
    node2 = next(n for n in updated_nodes if n["NODE_ID"] == 2)
    assert node2["CHECK"] == "FALSE"


@pytest.mark.asyncio
async def test_nodes_controller_flow(backend_server, monkeypatch):
    monkeypatch.setenv("BACKEND_URL", backend_server)
    monkeypatch.setenv("NODE_ID", "1")
    monkeypatch.setenv("NODE_HAS_BATTERY", "0")
    s = Settings()
    helpers = Helpers(s)
    # Mock ping in helpers so ping always succeeds
    helpers.ping = lambda host: type("Ping", (), {"returncode": 0})()

    bc = BackendController(s, helpers)
    # Ensure Node 2 has check=TRUE
    bc.update_node_check(2, "TRUE")

    nc = NodesController(s, bc, helpers)
    app = MockApplication()

    await nc.handle(app)

    # Verify that Node 1's heartbeat was saved
    node1 = next(n for n in bc.get_nodes() if n["NODE_ID"] == 1)
    assert node1["TS_LAST_NODE_WRITE"] != ""

    # Verify Node 2 was pinged
    node2 = next(n for n in bc.get_nodes() if n["NODE_ID"] == 2)
    assert node2["TS_LAST_PING"] != ""
    assert node2["LAST_PING_RESULT"] == "success"
    assert node2["LAST_PING_BY"] == "NODE_1"


def test_nodes_controller_status_check(monkeypatch):
    s = Settings()
    helpers = Helpers(s)
    bc = BackendController(s, helpers)
    nc = NodesController(s, bc, helpers)

    # Empty or None should safely return offline
    assert nc._check_node_status("") == "offline"
    assert nc._check_node_status(None) == "offline"
    assert nc._check_node_status("invalid-date") == "offline"


@pytest.mark.asyncio
async def test_handlers_commands(backend_server, monkeypatch):
    from bot.Handlers import Handlers

    monkeypatch.setenv("BACKEND_URL", backend_server)
    monkeypatch.setenv("NODE_ID", "1")
    monkeypatch.setenv("NODE_DEBUG", "1")
    s = Settings()
    helpers = Helpers(s)

    handlers = Handlers(s, helpers)
    update = MockUpdate()

    # Disable command for self
    await handlers.disable_command(update, MockContext())
    node1 = next(n for n in handlers.storage.get_nodes() if n["NODE_ID"] == 1)
    assert node1["CHECK"] == "FALSE"

    # Enable command for self
    await handlers.enable_command(update, MockContext())
    node1 = next(n for n in handlers.storage.get_nodes() if n["NODE_ID"] == 1)
    assert node1["CHECK"] == "TRUE"

    # Disable other nodes command
    context = MockContext(args=["2"])
    await handlers.disable_nodes_command(update, context)
    node2 = next(n for n in handlers.storage.get_nodes() if n["NODE_ID"] == 2)
    assert node2["CHECK"] == "FALSE"

    # Enable other nodes command
    await handlers.enable_nodes_command(update, context)
    node2 = next(n for n in handlers.storage.get_nodes() if n["NODE_ID"] == 2)
    assert node2["CHECK"] == "TRUE"
