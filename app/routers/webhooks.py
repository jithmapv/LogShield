from fastapi import APIRouter, Header, HTTPException, Request

from app.webhooks import verify_hmac

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.post("/ingest")
async def receive_webhook(request: Request, x_hub_signature: str | None = Header(default=None)) -> dict[str, str]:
    body = await request.body()
    if not verify_hmac(body, x_hub_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    return {"status": "accepted"}