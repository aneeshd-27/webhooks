#!/usr/bin/env python3
"""
Startup script for Brevo Webhook Handler
"""
import uvicorn
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 3000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"🚀 Starting Brevo Webhook Handler")
    print(f"📡 Server: http://{host}:{port}")
    print(f"📋 API Docs: http://{host}:{port}/docs")
    print(f"❤️ Health Check: http://{host}:{port}/health")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
