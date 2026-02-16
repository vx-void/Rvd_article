from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class APIKeyInfo(BaseModel):
    key_id: str
    name: str
    created_at: datetime
    last_used: Optional[datetime] = None
    request_count: int = 0
    rate_limit: int = 30
    is_active: bool = True


class APIKeyUsage(BaseModel):
    key_id: str
    total_requests: int
    requests_last_hour: int
    requests_last_day: int
    average_latency_ms: float