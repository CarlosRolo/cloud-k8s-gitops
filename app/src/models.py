from pydantic import BaseModel
from typing import Optional

class NetworkDevice(BaseModel):
    id: Optional[int] = None
    hostname: str
    ip_address: str
    device_type: str
    status: str = "active"

class HealthResponse(BaseModel):
    status: str
    version: str
    cluster: str
