#!/usr/bin/env python3
"""
Startup script for Brevo Transactional Webhook Handler
"""
import uvicorn
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("TRANSACTIONAL_PORT", 3001))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"🚀 Starting Brevo Transactional Webhook Handler")
    print(f"📡 Server: http://{host}:{port}")
    print(f"📋 API Docs: http://{host}:{port}/docs")
    print(f"❤️ Health Check: http://{host}:{port}/health")
    print(f"🎯 Webhook Endpoint: http://{host}:{port}/webhook/brevo/transactional")
    
    # Start the server
    uvicorn.run(
        "transactional_main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
