import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_list_devices():
    r = client.get("/devices")
    assert r.status_code == 200
    assert len(r.json()) == 3

def test_get_device():
    r = client.get("/devices/1")
    assert r.status_code == 200
    assert r.json()["hostname"] == "router-core-01"

def test_get_device_not_found():
    r = client.get("/devices/999")
    assert r.status_code == 404

def test_create_device():
    r = client.post("/devices", json={
        "hostname": "ap-floor-01",
        "ip_address": "10.0.3.1",
        "device_type": "access-point"
    })
    assert r.status_code == 201
    assert r.json()["id"] == 4
