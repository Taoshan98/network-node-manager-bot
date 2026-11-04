import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from backend.models import (
    Node,
    HeartbeatRequest,
    PingUpdateRequest,
    CheckUpdateRequest,
    NodeCreateOrUpdateRequest,
    HeartbeatLog,
)
from backend.storage import storage

app = FastAPI(
    title="Network Node Manager Bot - Backend API",
    description="Serverless REST API backend for managing network nodes and status updates.",
    version="1.0.0",
)

# Enable CORS for dashboard/management integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_api_key(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
):
    expected_key = os.getenv("BACKEND_API_KEY")
    if not expected_key:
        return True

    token = x_api_key
    if not token and authorization:
        parts = authorization.split(" ")
        token = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else parts[0]

    if token != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return True


@app.get("/")
@app.get("/api")
def root():
    return {
        "service": "Network Node Manager Backend",
        "status": "online",
        "documentation": "/docs",
        "nodes_count": len(storage.get_all_nodes()),
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/nodes", response_model=List[Node], dependencies=[Depends(verify_api_key)])
def get_nodes():
    return storage.get_all_nodes()


@app.get("/api/nodes/{node_id}", response_model=Node, dependencies=[Depends(verify_api_key)])
def get_node(node_id: int):
    node = storage.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return node


@app.post("/api/nodes", response_model=Node, dependencies=[Depends(verify_api_key)])
def create_or_upsert_node(node: NodeCreateOrUpdateRequest):
    if node.NODE_ID is None:
        raise HTTPException(status_code=400, detail="NODE_ID is required")
    dump_fn = getattr(node, "model_dump", getattr(node, "dict"))
    data = {k: v for k, v in dump_fn().items() if v is not None}
    return storage.upsert_node(data)


@app.put("/api/nodes/{node_id}", response_model=Node, dependencies=[Depends(verify_api_key)])
@app.patch("/api/nodes/{node_id}", response_model=Node, dependencies=[Depends(verify_api_key)])
def update_node(node_id: int, payload: NodeCreateOrUpdateRequest):
    node = storage.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    dump_fn = getattr(payload, "model_dump", getattr(payload, "dict"))
    data = {k: v for k, v in dump_fn().items() if v is not None}
    data["NODE_ID"] = node_id
    return storage.upsert_node(data)


@app.delete("/api/nodes/{node_id}", dependencies=[Depends(verify_api_key)])
def delete_node(node_id: int):
    deleted = storage.delete_node(node_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return {"status": "deleted", "node_id": node_id}


@app.post("/api/nodes/{node_id}/heartbeat", dependencies=[Depends(verify_api_key)])
def record_heartbeat(node_id: int, payload: HeartbeatRequest):
    updated = storage.update_heartbeat(
        node_id=node_id,
        timestamp=payload.timestamp,
        wan_ip=payload.wan_ip,
        battery_status=payload.battery_status,
    )
    return {"status": "ok", "node": updated}


@app.post("/api/nodes/{node_id}/ping", dependencies=[Depends(verify_api_key)])
def record_ping(node_id: int, payload: PingUpdateRequest):
    updated = storage.update_ping(
        node_id=node_id,
        ping_ts=payload.ping_ts,
        ping_result=payload.ping_result,
        last_ping_by=payload.last_ping_by,
        status=payload.status,
    )
    if not updated:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return {"status": "ok", "node": updated}


@app.post("/api/nodes/{node_id}/check", dependencies=[Depends(verify_api_key)])
@app.patch("/api/nodes/{node_id}/check", dependencies=[Depends(verify_api_key)])
def update_check(node_id: int, payload: CheckUpdateRequest):
    updated = storage.update_check(node_id=node_id, check=payload.check)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return {"status": "ok", "node": updated}


@app.get("/api/nodes/{node_id}/logs", response_model=List[HeartbeatLog], dependencies=[Depends(verify_api_key)])
def get_node_logs(node_id: int, limit: int = 50):
    node = storage.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return storage.get_logs(node_id=node_id, limit=limit)
