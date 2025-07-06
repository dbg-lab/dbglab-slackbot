# Slack Chatbot with OpenAI Integration

A lightweight Python Slack chatbot that responds to mentions by sending user messages to OpenAI's Chat Completions API and posting the responses back to Slack threads.

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed system architecture, data flow, and component descriptions
- **[TASKS.md](TASKS.md)**: Step-by-step implementation plan for building the MVP

## Features

- **Slack Integration**: Responds to app mentions (@bot) in Slack channels
- **OpenAI Integration**: Uses GPT-4 (or configurable model) for intelligent responses
- **Thread Support**: Automatically replies in the same thread as the original message
- **Stateless Design**: No conversation history or persistent state for simplicity
- **Serverless Ready**: Designed for easy deployment to AWS Lambda or similar platforms

## Tech Stack

- **Language**: Python 3.9+
- **Web Framework**: Flask
- **Slack SDK**: Slack Bolt for Python (Flask adapter)
- **OpenAI SDK**: openai-python
- **Environment Management**: python-dotenv

## Prerequisites

- Python 3.9 or higher
- Slack App with Bot Token and Signing Secret
- OpenAI API key
- ngrok (for local development)

## Installation

1. **Clone the repository**:
   nested_code_snippet_bash-replace_with-```bash
   git clone <repository-url>
   cd dbglab-slackbot
   close_nested_code_snippet-replace_with-```

2. **Create a virtual environment**:
   nested_code_snippet_bash-replace_with-```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   close_nested_code_snippet-replace_with-```

3. **Install dependencies**:
   nested_code_snippet_bash-replace_with-```bash
   pip install -r requirements.txt
   close_nested_code_snippet-replace_with-```

4. **Set up environment variables**:
   nested_code_snippet_bash-replace_with-```bash
   cp .env.example .env
   close_nested_code_snippet-replace_with-```

   Edit `.env` with your actual values (see Environment Variables section below).

## Environment Variables

Create a `.env` file in the root directory with the following variables:

nested_code_snippet_bash-replace_with-```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo for faster/cheaper responses

# Flask Configuration
FLASK_ENV=development
FLASK_PORT=3000

# Optional: Logging
LOG_LEVEL=INFO
close_nested_code_snippet-replace_with-```

### How to Get These Values

#### Slack App Setup
1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Create a new app or use an existing one
3. Go to "OAuth & Permissions" → copy the "Bot User OAuth Token" (`SLACK_BOT_TOKEN`)
4. Go to "Basic Information" → copy the "Signing Secret" (`SLACK_SIGNING_SECRET`)
5. In "OAuth & Permissions", add these Bot Token Scopes:
   - `app_mentions:read`
   - `chat:write`
   - `channels:read`
   - `im:read`
   - `groups:read`
   - `mpim:read`

#### OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`) and use it as `OPENAI_API_KEY`

## Local Development

### 1. Start the Flask Application

nested_code_snippet_bash-replace_with-```bash
python main.py
close_nested_code_snippet-replace_with-```

The app will start on `http://localhost:3000` by default.

### 2. Set up ngrok for Slack Webhooks

In a new terminal window:

nested_code_snippet_bash-replace_with-```bash
ngrok http 3000
close_nested_code_snippet-replace_with-```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`).

### 3. Configure Slack App Webhook

1. Go to your Slack app settings
2. Navigate to "Event Subscriptions"
3. Enable events and set the Request URL to: `https://your-ngrok-url.ngrok.io/slack/events`
4. Subscribe to bot events:
   - `app_mention`
   - `message.channels` (optional, for direct messages)
5. Save changes and reinstall the app to your workspace

### 4. Test the Bot

1. Invite the bot to a channel: `/invite @your-bot-name`
2. Mention the bot: `@your-bot-name Hello, how are you?`
3. The bot should respond with an OpenAI-generated message in the same thread

## Project Structure

```
slackbot/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── slack_handler.py     # Slack event handlers
│   ├── services/
│   │   ├── __init__.py
│   │   ├── openai_service.py    # OpenAI API integration
│   │   └── slack_service.py     # Slack API utilities
│   └── utils/
│       ├── __init__.py
│       └── config.py            # Configuration management
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore patterns
├── README.md                    # This file
└── ARCHITECTURE.md              # Architecture documentation
```

## Deployment

### AWS Lambda (Serverless)

The application is designed to be serverless-ready. For AWS Lambda deployment:

1. Install serverless framework or use AWS SAM
2. Configure API Gateway for the webhook endpoint
3. Set environment variables in Lambda configuration
4. Deploy with appropriate IAM roles

### Traditional Hosting

For traditional hosting (EC2, DigitalOcean, etc.):

1. Set up a reverse proxy (nginx)
2. Use a production WSGI server (gunicorn)
3. Configure SSL/TLS certificates
4. Set up process management (systemd, supervisor)

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check that the webhook URL is correct and accessible
2. **Authentication errors**: Verify Slack tokens and signing secret
3. **OpenAI errors**: Check API key and quota limits
4. **ngrok issues**: Ensure ngrok is running and URL is updated in Slack

### Debugging

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.

### Health Check

The application includes a health check endpoint at `/health` for monitoring.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the [architecture documentation](ARCHITECTURE.md)
- Follow the [implementation tasks](TASKS.md) for development
- Open an issue on GitHub 