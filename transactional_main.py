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
    title="Brevo Transactional Webhook Handler",
    description="Webhook handler for Brevo transactional email events",
    version="1.0.0"
)

# Configuration
PORT = int(os.getenv("TRANSACTIONAL_PORT", 3001))  # Different port from campaign webhook
BREVO_WEBHOOK_SECRET = os.getenv("BREVO_TRANSACTIONAL_WEBHOOK_SECRET", "your_transactional_webhook_secret_here")

# Check if webhook secret is properly configured
if BREVO_WEBHOOK_SECRET == "your_transactional_webhook_secret_here":
    logger.warning("⚠️ Using default transactional webhook secret! Please set BREVO_TRANSACTIONAL_WEBHOOK_SECRET in your .env file or environment variables.")

# Pydantic models for request validation
class TransactionalWebhookEvent(BaseModel):
    event: str
    data: Dict[str, Any]

# Webhook signature verification dependency
async def verify_webhook_signature(request: Request):
    """Verify Brevo transactional webhook signature"""
    signature = request.headers.get("x-brevo-signature")
    
    if not signature or not BREVO_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Missing signature or transactional webhook secret")
    
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

# Event handlers for different transactional events
class TransactionalEventHandlers:
    @staticmethod
    def handle_sent(data: Dict[str, Any]):
        logger.info("📤 Transactional email sent: %s", {
            "email": data.get("email"),
            "message_id": data.get("message_id"),
            "template_id": data.get("template_id"),
            "timestamp": data.get("timestamp"),
            "subject": data.get("subject")
        })
        # Add your sent tracking logic here
    
    @staticmethod
    def handle_clicked(data: Dict[str, Any]):
        logger.info("🔗 Transactional link clicked: %s", {
            "email": data.get("email"),
            "message_id": data.get("message_id"),
            "timestamp": data.get("timestamp"),
            "link_url": data.get("link_url"),
            "user_agent": data.get("user_agent"),
            "ip_address": data.get("ip_address")
        })
        # Add your click tracking logic here
    
    @staticmethod
    def handle_delivered(data: Dict[str, Any]):
        logger.info("✅ Transactional email delivered: %s", {
            "email": data.get("email"),
            "message_id": data.get("message_id"),
            "timestamp": data.get("timestamp"),
            "template_id": data.get("template_id")
        })
        # Add your delivery confirmation logic here
    
    @staticmethod
    def handle_soft_bounced(data: Dict[str, Any]):
        logger.info("⚠️ Transactional soft bounce: %s", {
            "email": data.get("email"),
            "message_id": data.get("message_id"),
            "timestamp": data.get("timestamp"),
            "bounce_reason": data.get("bounce_reason"),
            "error_code": data.get("error_code")
        })
        # Add your soft bounce handling logic here
        # Consider retrying later
    
    @staticmethod
    def handle_spam(data: Dict[str, Any]):
        logger.info("📧 Transactional email marked as spam: %s", {
            "email": data.get("email"),
            "message_id": data.get("message_id"),
            "timestamp": data.get("timestamp"),
            "reason": data.get("reason", "Not specified")
        })
        # Add your spam handling logic here
    
    @staticmethod
    def handle_first_opening(data: Dict[str, Any]):
        logger.info("👀 First opening of transactional email: %s", {
            "email": data.get("email"),
            "message_id": data.get("message_id"),
            "timestamp": data.get("timestamp"),
            "user_agent": data.get("user_agent"),
            "ip_address": data.get("ip_address")
        })
        # Add your first opening tracking logic here
    
    @staticmethod
    def handle_hard_bounced(data: Dict[str, Any]):
        logger.info("❌ Transactional hard bounce: %s", {
            "email": data.get("email"),
            "message_id": data.get("message_id"),
            "timestamp": data.get("timestamp"),
            "bounce_reason": data.get("bounce_reason"),
            "error_code": data.get("error_code")
        })
        # Add your hard bounce handling logic here
        # Consider removing email from your list
    
    @staticmethod
    def handle_opened(data: Dict[str, Any]):
        logger.info("👀 Transactional email opened: %s", {
            "email": data.get("email"),
            "message_id": data.get("message_id"),
            "timestamp": data.get("timestamp"),
            "user_agent": data.get("user_agent"),
            "ip_address": data.get("ip_address")
        })
        # Add your open tracking logic here
    
    @staticmethod
    def handle_invalid_email(data: Dict[str, Any]):
        logger.info("❌ Invalid email address: %s", {
            "email": data.get("email"),
            "message_id": data.get("message_id"),
            "timestamp": data.get("timestamp"),
            "error_reason": data.get("error_reason"),
            "error_code": data.get("error_code")
        })
        # Add your invalid email handling logic here
        # Remove invalid email from your list
    
    @staticmethod
    def handle_blocked(data: Dict[str, Any]):
        logger.info("🚫 Transactional email blocked: %s", {
            "email": data.get("email"),
            "message_id": data.get("message_id"),
            "timestamp": data.get("timestamp"),
            "block_reason": data.get("block_reason"),
            "block_type": data.get("block_type")
        })
        # Add your blocked email handling logic here
    
    @staticmethod
    def handle_error(data: Dict[str, Any]):
        logger.info("🚨 Transactional email error: %s", {
            "email": data.get("email"),
            "message_id": data.get("message_id"),
            "timestamp": data.get("timestamp"),
            "error_message": data.get("error_message"),
            "error_code": data.get("error_code")
        })
        # Add your error handling logic here
    
    @staticmethod
    def handle_unsubscribed(data: Dict[str, Any]):
        logger.info("🚫 Transactional unsubscribe: %s", {
            "email": data.get("email"),
            "message_id": data.get("message_id"),
            "timestamp": data.get("timestamp"),
            "unsubscribe_url": data.get("unsubscribe_url")
        })
        # Add your unsubscribe handling logic here
        # Remove email from your mailing list

# Event handler mapping for transactional events
TRANSACTIONAL_EVENT_HANDLERS = {
    "sent": TransactionalEventHandlers.handle_sent,
    "clicked": TransactionalEventHandlers.handle_clicked,
    "delivered": TransactionalEventHandlers.handle_delivered,
    "soft_bounced": TransactionalEventHandlers.handle_soft_bounced,
    "spam": TransactionalEventHandlers.handle_spam,
    "first_opening": TransactionalEventHandlers.handle_first_opening,
    "hard_bounced": TransactionalEventHandlers.handle_hard_bounced,
    "opened": TransactionalEventHandlers.handle_opened,
    "invalid_email": TransactionalEventHandlers.handle_invalid_email,
    "blocked": TransactionalEventHandlers.handle_blocked,
    "error": TransactionalEventHandlers.handle_error,
    "unsubscribed": TransactionalEventHandlers.handle_unsubscribed
}

@app.post("/webhook/brevo/transactional/test")
async def brevo_transactional_webhook_test(request: Request):
    """Test transactional webhook endpoint without signature verification"""
    try:
        # Parse JSON body
        webhook_data = await request.json()
        event = webhook_data.get("event")
        # For transactional webhooks, the data is often in the root of the payload
        data = webhook_data.get("data", webhook_data)
        
        logger.info("🎯 Received Brevo transactional webhook test event: %s", event)
        logger.info("📊 Event data: %s", json.dumps(data, indent=2))
        
        # Check if we have a handler for this event
        if event in TRANSACTIONAL_EVENT_HANDLERS:
            TRANSACTIONAL_EVENT_HANDLERS[event](data)
        else:
            logger.warning("⚠️ No handler found for transactional event: %s", event)
        
        # Always respond with 200 OK to acknowledge receipt
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Transactional test webhook received successfully",
                "event": event
            }
        )
        
    except Exception as e:
        logger.error("❌ Error processing transactional test webhook: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/webhook/brevo/transactional")
async def brevo_transactional_webhook(
    request: Request,
    body: bytes = Depends(verify_webhook_signature)
):
    """Main webhook endpoint for Brevo transactional email events"""
    try:
        # Parse JSON body
        webhook_data = json.loads(body.decode())
        event = webhook_data.get("event")
        data = webhook_data.get("data", {})
        
        logger.info("🎯 Received Brevo transactional webhook event: %s", event)
        logger.info("📊 Event data: %s", json.dumps(data, indent=2))
        
        # Check if we have a handler for this event
        if event in TRANSACTIONAL_EVENT_HANDLERS:
            TRANSACTIONAL_EVENT_HANDLERS[event](data)
        else:
            logger.warning("⚠️ No handler found for transactional event: %s", event)
        
        # Always respond with 200 OK to acknowledge receipt
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Transactional webhook received successfully",
                "event": event
            }
        )
        
    except json.JSONDecodeError as e:
        logger.error("❌ Invalid JSON in transactional webhook payload: %s", str(e))
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error("❌ Error processing transactional webhook: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "OK",
            "timestamp": datetime.now().isoformat(),
            "service": "Brevo Transactional Webhook Handler"
        }
    )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return JSONResponse(
        status_code=200,
        content={
            "message": "Brevo Transactional Webhook Handler is running",
            "endpoints": {
                "webhook": "POST /webhook/brevo/transactional",
                "health": "GET /health"
            },
            "supported_events": list(TRANSACTIONAL_EVENT_HANDLERS.keys())
        }
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Brevo transactional webhook handler on port %s", PORT)
    logger.info("📡 Webhook endpoint: http://localhost:%s/webhook/brevo/transactional", PORT)
    logger.info("❤️ Health check: http://localhost:%s/health", PORT)
    logger.info("📋 Supported transactional events: %s", ", ".join(TRANSACTIONAL_EVENT_HANDLERS.keys()))
    
    uvicorn.run(
        "transactional_main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        log_level="info"
    )
