# Brevo Webhook Handlers (FastAPI)

This project provides separate webhook handlers for Brevo (formerly Sendinblue) campaign and transactional email events using FastAPI.

## 📧 Campaign Webhook Handler

Handles webhook events for email campaigns.

### Supported Campaign Events:
- **Marked as Spam** (`spam`)
- **Opened** (`opened`) 
- **Clicked** (`clicked`)
- **Hard Bounced** (`hard_bounced`)
- **Soft Bounced** (`soft_bounced`)
- **Delivered** (`delivered`)
- **Unsubscribe** (`unsubscribe`)

### Endpoint: `POST /webhook/brevo` (Port 3000)

## 📨 Transactional Webhook Handler

Handles webhook events for transactional emails.

### Supported Transactional Events:
- **Sent** (`sent`)
- **Clicked** (`clicked`)
- **Delivered** (`delivered`)
- **Soft Bounced** (`soft_bounced`)
- **Spam** (`spam`)
- **First Opening** (`first_opening`)
- **Hard Bounced** (`hard_bounced`)
- **Opened** (`opened`)
- **Invalid Email** (`invalid_email`)
- **Blocked** (`blocked`)
- **Error** (`error`)
- **Unsubscribed** (`unsubscribed`)

### Endpoint: `POST /webhook/brevo/transactional` (Port 3001)

### Meta Transactional

- Verify (GET): `GET /webhook/meta/transactional?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...`
- Webhook (POST): `POST /webhook/meta/transactional`
- Port: `META_TRANSACTIONAL_PORT` (default 4001)

## 🚀 Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
# Copy the example file
cp env.example .env
# Then edit .env with your actual values
```

3. **Start the servers:**

**Campaign Webhook (Port 3000):**
```bash
python main.py
# OR
python start.py
```

**Transactional Webhook (Port 3001):**
```bash
python transactional_main.py
# OR
python start_transactional.py
```

**Both servers simultaneously:**
```bash
# Terminal 1
python start.py

# Terminal 2
python start_transactional.py
```

## 🔧 Environment Variables

```env
# Campaign Webhook Configuration
PORT=3000
BREVO_WEBHOOK_SECRET=your_campaign_webhook_secret_here

# Transactional Webhook Configuration
TRANSACTIONAL_PORT=3001
BREVO_TRANSACTIONAL_WEBHOOK_SECRET=your_transactional_webhook_secret_here

# General Configuration
HOST=0.0.0.0
RELOAD=true
```

## 🧪 Testing

**Test Campaign Webhook:**
```bash
python test_webhook.py
```

**Test Transactional Webhook:**
```bash
python test_transactional_webhook.py
```

## 📚 API Documentation

Both webhook handlers automatically generate interactive API documentation:

### Campaign Webhook:
- **Swagger UI**: `http://localhost:3000/docs`
- **ReDoc**: `http://localhost:3000/redoc`

### Transactional Webhook:
- **Swagger UI**: `http://localhost:3001/docs`
- **ReDoc**: `http://localhost:3001/redoc`

## 🔗 Webhook URLs

Configure these URLs in your Brevo account settings:

- **Campaign Webhook**: `http://your-domain.com/webhook/brevo`
- **Transactional Webhook**: `http://your-domain.com/webhook/brevo/transactional`

## 🏥 Health Checks

- **Campaign Health**: `http://localhost:3000/health`
- **Transactional Health**: `http://localhost:3001/health`

## 🔒 Security Features

- ✅ Webhook signature verification using HMAC-SHA256
- ✅ Separate secrets for campaign and transactional webhooks
- ✅ Request body validation with Pydantic
- ✅ Comprehensive error handling and logging
- ✅ Structured logging with emojis for easy monitoring

## 📊 Event Handling

Each webhook handler includes:
- Individual event handlers for all supported events
- Detailed logging with relevant data extraction
- Placeholder logic for custom business rules
- Proper error handling and response formatting

## 🚀 Deployment

Both webhook handlers can be deployed independently:

```bash
# Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 3000
uvicorn transactional_main:app --host 0.0.0.0 --port 3001

# Using the startup scripts
python start.py
python start_transactional.py
```

## 📝 File Structure

```
webhooks/
├── main.py                      # Campaign webhook handler
├── transactional_main.py        # Transactional webhook handler
├── start.py                     # Campaign webhook startup script
├── start_transactional.py       # Transactional webhook startup script
├── test_webhook.py              # Campaign webhook tests
├── test_transactional_webhook.py # Transactional webhook tests
├── setup.py                     # Environment setup script
├── requirements.txt             # Python dependencies
├── env.example                  # Environment variables template
└── README.md                    # This documentation
```
