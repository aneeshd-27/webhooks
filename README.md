# Brevo Webhook Handler (FastAPI)

This project handles webhook events from Brevo (formerly Sendinblue) for email campaigns using FastAPI.

## Supported Events

- **Marked as Spam**: When an email is marked as spam
- **Opened**: When an email is opened by the recipient
- **Clicked**: When a link in the email is clicked
- **Hard Bounced**: When an email bounces due to permanent issues
- **Soft Bounced**: When an email bounces due to temporary issues
- **Delivered**: When an email is successfully delivered
- **Unsubscribe**: When a recipient unsubscribes

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables. You have several options:

**Option A: Create a `.env` file (recommended):**
```bash
# Copy the example file
cp env.example .env
# Then edit .env with your actual values
```

**Option B: Set environment variables directly:**
```bash
# Windows PowerShell
$env:PORT="3000"
$env:BREVO_WEBHOOK_SECRET="your_actual_webhook_secret"

# Windows Command Prompt
set PORT=3000
set BREVO_WEBHOOK_SECRET=your_actual_webhook_secret

# Linux/Mac
export PORT=3000
export BREVO_WEBHOOK_SECRET=your_actual_webhook_secret
```

**Option C: Create a `.env` file manually:**
Create a file named `.env` in your project root with:
```
PORT=3000
BREVO_WEBHOOK_SECRET=your_actual_webhook_secret
```

3. Start the server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

## Environment Variables

- `PORT`: Server port (default: 3000)
- `BREVO_WEBHOOK_SECRET`: Your Brevo webhook secret for signature verification

## Webhook Endpoint

The webhook endpoint is available at: `POST /webhook/brevo`

Make sure to configure this URL in your Brevo account settings.

## Testing

Run the test suite to verify all webhook events:

```bash
python test_webhook.py
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:3000/docs`
- **ReDoc**: `http://localhost:3000/redoc`

## Meta (Facebook/Instagram/WABA) Webhooks

Two parallel handlers are included for Meta webhooks with identical verification/signature logic to campaign vs transactional split:

- Campaign-like handler: `meta_main.py`
  - Verify (GET): `GET /webhook/meta?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...`
  - Webhook (POST): `POST /webhook/meta`
  - Port: `META_PORT` (default 4000)
- Transactional-like handler: `meta_transactional_main.py`
  - Verify (GET): `GET /webhook/meta/transactional?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...`
  - Webhook (POST): `POST /webhook/meta/transactional`
  - Port: `META_TRANSACTIONAL_PORT` (default 4001)

Both validate `X-Hub-Signature-256` using your Meta App Secret, and echo the `hub.challenge` when the verify token matches.

## Features

- ✅ FastAPI framework with automatic API documentation
- ✅ Webhook signature verification for security
- ✅ Comprehensive event handling for all 6 campaign events
- ✅ Structured logging with emojis for easy monitoring
- ✅ Health check endpoint for monitoring
- ✅ Async/await support for better performance
- ✅ Pydantic models for request validation
- ✅ Built-in test utilities
