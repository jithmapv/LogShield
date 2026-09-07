import hashlib
import hmac
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import get_settings


def verify_hmac(body: bytes, signature: str | None) -> bool:
    if not signature or not signature.startswith("sha256="):
        return False
    expected = hmac.new(get_settings().webhook_hmac_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature[7:], expected)


async def dispatch_incident(incident: dict[str, Any]) -> None:
    payload = {**incident, "timestamp": datetime.now(timezone.utc).isoformat(), "recommended_action": "throttle_source_ip"}
    async with httpx.AsyncClient(timeout=5) as client:
        for url in get_settings().webhook_url_list:
            try:
                await client.post(url, json=payload)
            except httpx.HTTPError:
                continue


def remediation_payload(source_ip: str) -> dict[str, Any]:
    return {"action": "temporary_ip_throttle", "source_ip": source_ip, "duration_seconds": 300}