from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
import hashlib
import hmac
import json
import os
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Meta Webhook Handler (Campaign)",
    description="Webhook handler for Meta subscriptions (e.g., Page/Messenger, WABA) - Campaign style",
    version="1.0.0"
)

# Configuration
PORT = int(os.getenv("META_PORT", 4000))
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "your_meta_verify_token_here")
META_APP_SECRET = os.getenv("META_APP_SECRET", "your_meta_app_secret_here")

if META_VERIFY_TOKEN == "your_meta_verify_token_here" or META_APP_SECRET == "your_meta_app_secret_here":
    logger.warning("⚠️ Using default Meta verify token or app secret! Please set META_VERIFY_TOKEN and META_APP_SECRET in your .env file or environment variables.")


def verify_x_hub_signature(body: bytes, signature_header: str, app_secret: str) -> bool:
    """Validate X-Hub-Signature-256 using Meta app secret."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    provided_sig_hex = signature_header.split("=", 1)[1]
    expected_sig = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(provided_sig_hex, expected_sig)


async def validate_meta_signature(request: Request):
    signature = request.headers.get("x-hub-signature-256")
    if not META_APP_SECRET:
        raise HTTPException(status_code=401, detail="Missing app secret")
    body = await request.body()
    if not verify_x_hub_signature(body, signature or "", META_APP_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")
    return body


@app.get("/webhook/meta")
async def meta_verify(mode: str | None = None, challenge: str | None = None, verify_token: str | None = None, hub_mode: str | None = None, hub_challenge: str | None = None, hub_verify_token: str | None = None):
    """
    Meta verification endpoint.
    Supports both modern (hub.*) and plain query params for convenience.
    """
    # Normalize param names
    mode_val = hub_mode or mode
    challenge_val = hub_challenge or challenge
    token_val = hub_verify_token or verify_token

    if mode_val == "subscribe" and token_val == META_VERIFY_TOKEN and challenge_val is not None:
        return PlainTextResponse(content=challenge_val, status_code=200)

    raise HTTPException(status_code=403, detail="Verification failed")


class CampaignEventHandlers:
    @staticmethod
    def handle_whatsapp(entry_change: Dict[str, Any]):
        logger.info("📲 WhatsApp change (campaign handler): %s", json.dumps(entry_change, indent=2))

    @staticmethod
    def handle_messenger(entry_change: Dict[str, Any]):
        logger.info("💬 Messenger change (campaign handler): %s", json.dumps(entry_change, indent=2))


@app.post("/webhook/meta")
async def meta_webhook(
    request: Request,
    body: bytes = Depends(validate_meta_signature)
):
    """Main webhook endpoint for Meta campaign-style events."""
    try:
        payload = json.loads(body.decode())
        logger.info("🎯 Received Meta webhook (campaign): %s", json.dumps(payload, indent=2))

        obj = payload.get("object")
        entries = payload.get("entry", [])

        for entry in entries:
            changes = entry.get("changes") or []
            messaging = entry.get("messaging") or []

            # WhatsApp Business Account changes
            if obj == "whatsapp_business_account" and changes:
                for change in changes:
                    CampaignEventHandlers.handle_whatsapp(change)

            # Messenger/Page events
            if obj in ("page", "instagram") and (changes or messaging):
                for change in (changes or []):
                    CampaignEventHandlers.handle_messenger(change)
                for event in (messaging or []):
                    CampaignEventHandlers.handle_messenger(event)

        return JSONResponse(status_code=200, content={"success": True})

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.exception("❌ Error processing Meta webhook (campaign)")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    return JSONResponse(status_code=200, content={
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "service": "Meta Webhook Handler (Campaign)"
    })


@app.get("/")
async def root():
    return JSONResponse(status_code=200, content={
        "message": "Meta Webhook Handler (Campaign) is running",
        "endpoints": {
            "verify": "GET /webhook/meta",
            "webhook": "POST /webhook/meta",
            "health": "GET /health"
        }
    })


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Meta webhook handler (campaign) on port %s", PORT)
    logger.info("📡 Verify endpoint: http://localhost:%s/webhook/meta?hub.mode=subscribe&hub.verify_token=...&hub.challenge=123", PORT)
    uvicorn.run(
        "meta_main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        log_level="info"
    )


