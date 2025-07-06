# Slack Chatbot Architecture

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Slack App     │    │   Flask App     │    │   OpenAI API    │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │ User      │  │    │  │ Slack     │  │    │  │ Chat      │  │
│  │ Messages  │  │    │  │ Handler   │  │    │  │ Completion│  │
│  │ @mention  │  │────┼──┤           │  │────┼──┤ API       │  │
│  │           │  │    │  │           │  │    │  │           │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │                 │
│  │ Bot       │  │    │  │ Response  │  │    │                 │
│  │ Response  │  │────┼──┤ Handler   │  │    │                 │
│  │ in Thread │  │    │  │           │  │    │                 │
│  │           │  │    │  │           │  │    │                 │
│  └───────────┘  │    │  └───────────┘  │    │                 │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Data Flow

1. **Slack → Flask**: User mentions bot in Slack → Slack sends webhook to Flask app
2. **Flask → OpenAI**: Flask extracts message content → Sends to OpenAI Chat Completions API
3. **OpenAI → Flask**: OpenAI returns generated response → Flask receives the response
4. **Flask → Slack**: Flask posts response back to Slack in the same thread

## Proposed File Structure

```
slackbot/
├── app/
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── slack_handler.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── openai_service.py
│   │   └── slack_service.py
│   └── utils/
│       ├── __init__.py
│       └── config.py
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── ARCHITECTURE.md
```

## Component Descriptions

### Core Files

- **`main.py`**: Application entry point, initializes Flask app and Slack Bolt adapter
- **`requirements.txt`**: Python dependencies (Flask, slack-bolt, openai, python-dotenv)
- **`.env.example`**: Template for environment variables
- **`.gitignore`**: Git ignore patterns for Python projects

### App Directory Structure

#### `app/__init__.py`
- Flask application factory
- Slack Bolt app initialization
- Route registration

#### `app/handlers/slack_handler.py`
- Slack event handlers (app_mentions, messages)
- Message processing logic
- Thread management

#### `app/services/openai_service.py`
- OpenAI API client wrapper
- Chat completion request handling
- Response formatting

#### `app/services/slack_service.py`
- Slack API client wrapper
- Message posting utilities
- Thread reply handling

#### `app/utils/config.py`
- Environment variable management
- Configuration validation
- Default settings

## State Management

**Stateless Design**: This architecture is intentionally stateless to keep it lightweight and serverless-friendly.

- **No Persistent State**: No database or session storage
- **No Conversation History**: Each message is processed independently
- **Thread Context**: Slack handles thread context automatically
- **Configuration**: Environment variables only

## Service Connections

### Slack Integration
- **Webhook URL**: Slack sends events to Flask app via HTTP POST
- **Authentication**: Slack signing secret for request verification
- **Bot Token**: OAuth token for posting messages back to Slack

### OpenAI Integration
- **API Key**: OpenAI API key for authentication
- **HTTP Client**: Direct REST API calls via openai-python SDK
- **Model**: GPT-4 (configurable via environment variable)

### Flask Server
- **Port**: Configurable (default 3000 for local dev)
- **Endpoints**: 
  - `/slack/events` - Slack webhook endpoint
  - `/health` - Health check endpoint
- **Middleware**: Request logging, error handling

## Deployment Considerations

### Local Development
- Flask development server
- ngrok for Slack webhook URL
- Environment variables via .env file

### Production (AWS Lambda)
- Serverless Flask adapter
- Environment variables via Lambda configuration
- API Gateway for webhook endpoint
- No persistent storage required due to stateless design

## Security

- **Request Verification**: Slack signing secret validation
- **Environment Variables**: Sensitive data stored in environment
- **HTTPS**: Required for Slack webhooks (handled by deployment platform)
- **Rate Limiting**: Handled by Slack and OpenAI APIs 