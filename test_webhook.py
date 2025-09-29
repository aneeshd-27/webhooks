import asyncio
import json
import hmac
import hashlib
from datetime import datetime
import httpx

# Sample webhook payloads for testing
SAMPLE_PAYLOADS = {
    "spam": {
        "event": "spam",
        "data": {
            "email": "user@example.com",
            "campaign_id": "12345",
            "timestamp": datetime.now().isoformat(),
            "reason": "User marked email as spam"
        }
    },
    "opened": {
        "event": "opened",
        "data": {
            "email": "user@example.com",
            "campaign_id": "12345",
            "timestamp": datetime.now().isoformat(),
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "ip_address": "192.168.1.1"
        }
    },
    "clicked": {
        "event": "clicked",
        "data": {
            "email": "user@example.com",
            "campaign_id": "12345",
            "timestamp": datetime.now().isoformat(),
            "link_url": "https://example.com/product",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "ip_address": "192.168.1.1"
        }
    },
    "hard_bounced": {
        "event": "hard_bounced",
        "data": {
            "email": "invalid@example.com",
            "campaign_id": "12345",
            "timestamp": datetime.now().isoformat(),
            "bounce_reason": "Invalid email address",
            "error_code": "550"
        }
    },
    "soft_bounced": {
        "event": "soft_bounced",
        "data": {
            "email": "user@example.com",
            "campaign_id": "12345",
            "timestamp": datetime.now().isoformat(),
            "bounce_reason": "Mailbox full",
            "error_code": "452"
        }
    },
    "delivered": {
        "event": "delivered",
        "data": {
            "email": "user@example.com",
            "campaign_id": "12345",
            "timestamp": datetime.now().isoformat(),
            "message_id": "msg_123456789"
        }
    },
    "unsubscribe": {
        "event": "unsubscribe",
        "data": {
            "email": "user@example.com",
            "campaign_id": "12345",
            "timestamp": datetime.now().isoformat(),
            "unsubscribe_url": "https://example.com/unsubscribe?token=abc123"
        }
    }
}

def create_signature(payload: dict, secret: str) -> str:
    """Create webhook signature for payload"""
    payload_str = json.dumps(payload, separators=(',', ':'))
    return hmac.new(
        secret.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()

async def test_webhook(event_type: str, webhook_url: str, secret: str) -> dict:
    """Test webhook endpoint with specific event type"""
    payload = SAMPLE_PAYLOADS[event_type]
    signature = create_signature(payload, secret)
    
    headers = {
        "Content-Type": "application/json",
        "X-Brevo-Signature": signature
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=payload,
                headers=headers,
                timeout=10.0
            )
            result = response.json()
            print(f"✅ {event_type} event test: {result}")
            return result
    except httpx.RequestError as e:
        print(f"❌ {event_type} event test failed: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"❌ {event_type} event test failed: {e}")
        return {"error": str(e)}

async def test_all_events(
    webhook_url: str = "http://localhost:3000/webhook/brevo",
    secret: str = "test_secret"
):
    """Test all Brevo webhook events"""
    print("🧪 Testing all Brevo webhook events...\n")
    
    for event_type in SAMPLE_PAYLOADS.keys():
        await test_webhook(event_type, webhook_url, secret)
        await asyncio.sleep(1)  # Wait 1 second between tests
    
    print("\n✨ All tests completed!")

async def test_health_endpoint(base_url: str = "http://localhost:3000"):
    """Test health check endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health", timeout=5.0)
            result = response.json()
            print(f"❤️ Health check: {result}")
            return result
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return {"error": str(e)}

async def test_root_endpoint(base_url: str = "http://localhost:3000"):
    """Test root endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, timeout=5.0)
            result = response.json()
            print(f"🏠 Root endpoint: {result}")
            return result
    except Exception as e:
        print(f"❌ Root endpoint test failed: {e}")
        return {"error": str(e)}

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting comprehensive webhook tests...\n")
    
    # Test basic endpoints first
    await test_health_endpoint()
    await test_root_endpoint()
    
    print("\n" + "="*50 + "\n")
    
    # Test webhook events
    await test_all_events()

if __name__ == "__main__":
    asyncio.run(run_all_tests())
