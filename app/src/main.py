from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from .models import NetworkDevice, HealthResponse
from typing import List
import os

app = FastAPI(
    title="TeleOps Network API",
    description="Network device management API — CLOUD-06",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)

devices: List[NetworkDevice] = [
    NetworkDevice(id=1, hostname="router-core-01", ip_address="10.0.0.1", device_type="router"),
    NetworkDevice(id=2, hostname="switch-dist-01", ip_address="10.0.1.1", device_type="switch"),
    NetworkDevice(id=3, hostname="fw-edge-01",     ip_address="10.0.2.1", device_type="firewall"),
]

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        cluster=os.getenv("CLUSTER_NAME", "local")
    )

@app.get("/devices", response_model=List[NetworkDevice])
def list_devices():
    return devices

@app.get("/devices/{device_id}", response_model=NetworkDevice)
def get_device(device_id: int):
    for d in devices:
        if d.id == device_id:
            return d
    raise HTTPException(status_code=404, detail="Device not found")

@app.post("/devices", response_model=NetworkDevice, status_code=201)
def create_device(device: NetworkDevice):
    device.id = max(d.id for d in devices) + 1
    devices.append(device)
    return device

@app.delete("/devices/{device_id}", status_code=204)
def delete_device(device_id: int):
    for i, d in enumerate(devices):
        if d.id == device_id:
            devices.pop(i)
            return
    raise HTTPException(status_code=404, detail="Device not found")
