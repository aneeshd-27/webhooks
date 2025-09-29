from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
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
    title="Brevo Webhook Handler",
    description="Webhook handler for Brevo campaign events",
    version="1.0.0"
)

# Configuration
PORT = int(os.getenv("PORT", 3000))
BREVO_WEBHOOK_SECRET = os.getenv("BREVO_WEBHOOK_SECRET", "your_webhook_secret_here")

# Check if webhook secret is properly configured
if BREVO_WEBHOOK_SECRET == "your_webhook_secret_here":
    logger.warning("⚠️ Using default webhook secret! Please set BREVO_WEBHOOK_SECRET in your .env file or environment variables.")

# Pydantic models for request validation
class WebhookEvent(BaseModel):
    event: str
    data: Dict[str, Any]

# Webhook signature verification dependency
async def verify_webhook_signature(request: Request):
    """Verify Brevo webhook signature"""
    signature = request.headers.get("x-brevo-signature")
    
    if not signature or not BREVO_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Missing signature or webhook secret")
    
    # Get request body
    body = await request.body()
    
    # Create expected signature
    expected_signature = hmac.new(
        BREVO_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    return body

# Event handlers for different campaign events
class EventHandlers:
    @staticmethod
    def handle_spam(data: Dict[str, Any]):
        logger.info("📧 Email marked as spam: %s", {
            "email": data.get("email"),
            "campaign_id": data.get("campaign_id"),
            "timestamp": data.get("timestamp"),
            "reason": data.get("reason", "Not specified")
        })
        # Add your spam handling logic here
    
    @staticmethod
    def handle_opened(data: Dict[str, Any]):
        logger.info("👀 Email opened: %s", {
            "email": data.get("email"),
            "campaign_id": data.get("campaign_id"),
            "timestamp": data.get("timestamp"),
            "user_agent": data.get("user_agent"),
            "ip_address": data.get("ip_address")
        })
        # Add your open tracking logic here
    
    @staticmethod
    def handle_clicked(data: Dict[str, Any]):
        logger.info("🔗 Link clicked: %s", {
            "email": data.get("email"),
            "campaign_id": data.get("campaign_id"),
            "timestamp": data.get("timestamp"),
            "link_url": data.get("link_url"),
            "user_agent": data.get("user_agent"),
            "ip_address": data.get("ip_address")
        })
        # Add your click tracking logic here
    
    @staticmethod
    def handle_hard_bounced(data: Dict[str, Any]):
        logger.info("❌ Hard bounce: %s", {
            "email": data.get("email"),
            "campaign_id": data.get("campaign_id"),
            "timestamp": data.get("timestamp"),
            "bounce_reason": data.get("bounce_reason"),
            "error_code": data.get("error_code")
        })
        # Add your hard bounce handling logic here
        # Consider removing email from your list
    
    @staticmethod
    def handle_soft_bounced(data: Dict[str, Any]):
        logger.info("⚠️ Soft bounce: %s", {
            "email": data.get("email"),
            "campaign_id": data.get("campaign_id"),
            "timestamp": data.get("timestamp"),
            "bounce_reason": data.get("bounce_reason"),
            "error_code": data.get("error_code")
        })
        # Add your soft bounce handling logic here
        # Consider retrying later or flagging for review
    
    @staticmethod
    def handle_delivered(data: Dict[str, Any]):
        logger.info("✅ Email delivered: %s", {
            "email": data.get("email"),
            "campaign_id": data.get("campaign_id"),
            "timestamp": data.get("timestamp"),
            "message_id": data.get("message_id")
        })
        # Add your delivery confirmation logic here
    
    @staticmethod
    def handle_unsubscribe(data: Dict[str, Any]):
        logger.info("🚫 Unsubscribed: %s", {
            "email": data.get("email"),
            "campaign_id": data.get("campaign_id"),
            "timestamp": data.get("timestamp"),
            "unsubscribe_url": data.get("unsubscribe_url")
        })
        # Add your unsubscribe handling logic here
        # Remove email from your mailing list

# Event handler mapping
EVENT_HANDLERS = {
    "spam": EventHandlers.handle_spam,
    "opened": EventHandlers.handle_opened,
    "clicked": EventHandlers.handle_clicked,
    "hard_bounced": EventHandlers.handle_hard_bounced,
    "soft_bounced": EventHandlers.handle_soft_bounced,
    "delivered": EventHandlers.handle_delivered,
    "unsubscribe": EventHandlers.handle_unsubscribe
}

@app.post("/webhook/brevo/test")
async def brevo_webhook_test(request: Request):
    """Test webhook endpoint without signature verification"""
    try:
        # Parse JSON body
        webhook_data = await request.json()
        event = webhook_data.get("event")
        data = webhook_data.get("data", {})
        
        logger.info("🎯 Received Brevo webhook test event: %s", event)
        logger.info("📊 Event data: %s", json.dumps(data, indent=2))
        
        # Check if we have a handler for this event
        if EVENT_HANDLERS[event]:
            EVENT_HANDLERS[event](data)
        else:
            logger.warning("⚠️ No handler found for event: %s", event)
        
        # Always respond with 200 OK to acknowledge receipt
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Test webhook received successfully",
                "event": event
            }
        )
        
    except Exception as e:
        logger.error("❌ Error processing test webhook: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/webhook/brevo")
async def brevo_webhook(
    request: Request,
    body: bytes = Depends(verify_webhook_signature)
):
    """Main webhook endpoint for Brevo campaign events"""
    try:
        # Parse JSON body
        webhook_data = json.loads(body.decode())
        event = webhook_data.get("event")
        data = webhook_data.get("data", {})
        
        logger.info("🎯 Received Brevo webhook event: %s", event)
        logger.info("📊 Event data: %s", json.dumps(data, indent=2))
        
        # Check if we have a handler for this event
        if event in EVENT_HANDLERS:
            EVENT_HANDLERS[event](data)
        else:
            logger.warning("⚠️ No handler found for event: %s", event)
        
        # Always respond with 200 OK to acknowledge receipt
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Webhook received successfully",
                "event": event
            }
        )
        
    except json.JSONDecodeError as e:
        logger.error("❌ Invalid JSON in webhook payload: %s", str(e))
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error("❌ Error processing webhook: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "OK",
            "timestamp": datetime.now().isoformat(),
            "service": "Brevo Webhook Handler"
        }
    )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return JSONResponse(
        status_code=200,
        content={
            "message": "Brevo Webhook Handler is running",
            "endpoints": {
                "webhook": "POST /webhook/brevo",
                "test_webhook": "POST /webhook/brevo/test",
                "health": "GET /health"
            },
            "supported_events": list(EVENT_HANDLERS.keys())
        }
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Brevo webhook handler on port %s", PORT)
    logger.info("📡 Webhook endpoint: http://localhost:%s/webhook/brevo", PORT)
    logger.info("❤️ Health check: http://localhost:%s/health", PORT)
    logger.info("📋 Supported events: %s", ", ".join(EVENT_HANDLERS.keys()))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        log_level="info"
    )
