import asyncio
import json
import hmac
import hashlib
from datetime import datetime
import httpx

# Sample webhook payloads for transactional events
TRANSACTIONAL_SAMPLE_PAYLOADS = {
    "sent": {
        "event": "sent",
        "data": {
            "email": "user@example.com",
            "message_id": "msg_transactional_12345",
            "template_id": "template_001",
            "timestamp": datetime.now().isoformat(),
            "subject": "Welcome to our service!"
        }
    },
    "clicked": {
        "event": "clicked",
        "data": {
            "email": "user@example.com",
            "message_id": "msg_transactional_12345",
            "timestamp": datetime.now().isoformat(),
            "link_url": "https://example.com/verify-email",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "ip_address": "192.168.1.1"
        }
    },
    "delivered": {
        "event": "delivered",
        "data": {
            "email": "user@example.com",
            "message_id": "msg_transactional_12345",
            "timestamp": datetime.now().isoformat(),
            "template_id": "template_001"
        }
    },
    "soft_bounced": {
        "event": "soft_bounced",
        "data": {
            "email": "user@example.com",
            "message_id": "msg_transactional_12345",
            "timestamp": datetime.now().isoformat(),
            "bounce_reason": "Mailbox temporarily unavailable",
            "error_code": "452"
        }
    },
    "spam": {
        "event": "spam",
        "data": {
            "email": "user@example.com",
            "message_id": "msg_transactional_12345",
            "timestamp": datetime.now().isoformat(),
            "reason": "User marked transactional email as spam"
        }
    },
    "first_opening": {
        "event": "first_opening",
        "data": {
            "email": "user@example.com",
            "message_id": "msg_transactional_12345",
            "timestamp": datetime.now().isoformat(),
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "ip_address": "192.168.1.1"
        }
    },
    "hard_bounced": {
        "event": "hard_bounced",
        "data": {
            "email": "invalid@example.com",
            "message_id": "msg_transactional_12345",
            "timestamp": datetime.now().isoformat(),
            "bounce_reason": "Invalid email address",
            "error_code": "550"
        }
    },
    "opened": {
        "event": "opened",
        "data": {
            "email": "user@example.com",
            "message_id": "msg_transactional_12345",
            "timestamp": datetime.now().isoformat(),
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "ip_address": "192.168.1.1"
        }
    },
    "invalid_email": {
        "event": "invalid_email",
        "data": {
            "email": "notanemail",
            "message_id": "msg_transactional_12345",
            "timestamp": datetime.now().isoformat(),
            "error_reason": "Invalid email format",
            "error_code": "400"
        }
    },
    "blocked": {
        "event": "blocked",
        "data": {
            "email": "user@example.com",
            "message_id": "msg_transactional_12345",
            "timestamp": datetime.now().isoformat(),
            "block_reason": "Email address is blacklisted",
            "block_type": "blacklist"
        }
    },
    "error": {
        "event": "error",
        "data": {
            "email": "user@example.com",
            "message_id": "msg_transactional_12345",
            "timestamp": datetime.now().isoformat(),
            "error_message": "Template rendering failed",
            "error_code": "500"
        }
    },
    "unsubscribed": {
        "event": "unsubscribed",
        "data": {
            "email": "user@example.com",
            "message_id": "msg_transactional_12345",
            "timestamp": datetime.now().isoformat(),
            "unsubscribe_url": "https://example.com/unsubscribe?token=abc123"
        }
    }
}

def create_transactional_signature(payload: dict, secret: str) -> str:
    """Create webhook signature for transactional payload"""
    payload_str = json.dumps(payload, separators=(',', ':'))
    return hmac.new(
        secret.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()

async def test_transactional_webhook(event_type: str, webhook_url: str, secret: str) -> dict:
    """Test transactional webhook endpoint with specific event type"""
    payload = TRANSACTIONAL_SAMPLE_PAYLOADS[event_type]
    signature = create_transactional_signature(payload, secret)
    
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
            print(f"✅ {event_type} transactional event test: {result}")
            return result
    except httpx.RequestError as e:
        print(f"❌ {event_type} transactional event test failed: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"❌ {event_type} transactional event test failed: {e}")
        return {"error": str(e)}

async def test_all_transactional_events(
    webhook_url: str = "http://localhost:3001/webhook/brevo/transactional",
    secret: str = "test_transactional_secret"
):
    """Test all Brevo transactional webhook events"""
    print("🧪 Testing all Brevo transactional webhook events...\n")
    
    for event_type in TRANSACTIONAL_SAMPLE_PAYLOADS.keys():
        await test_transactional_webhook(event_type, webhook_url, secret)
        await asyncio.sleep(1)  # Wait 1 second between tests
    
    print("\n✨ All transactional tests completed!")

async def test_transactional_health_endpoint(base_url: str = "http://localhost:3001"):
    """Test transactional webhook health check endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health", timeout=5.0)
            result = response.json()
            print(f"❤️ Transactional health check: {result}")
            return result
    except Exception as e:
        print(f"❌ Transactional health check failed: {e}")
        return {"error": str(e)}

async def test_transactional_root_endpoint(base_url: str = "http://localhost:3001"):
    """Test transactional webhook root endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, timeout=5.0)
            result = response.json()
            print(f"🏠 Transactional root endpoint: {result}")
            return result
    except Exception as e:
        print(f"❌ Transactional root endpoint test failed: {e}")
        return {"error": str(e)}

async def run_all_transactional_tests():
    """Run all transactional webhook tests"""
    print("🚀 Starting comprehensive transactional webhook tests...\n")
    
    # Test basic endpoints first
    await test_transactional_health_endpoint()
    await test_transactional_root_endpoint()
    
    print("\n" + "="*50 + "\n")
    
    # Test webhook events
    await test_all_transactional_events()

if __name__ == "__main__":
    asyncio.run(run_all_transactional_tests())
