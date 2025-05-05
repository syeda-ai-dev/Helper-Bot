# Helper Bot

A simple instruction-based chatbot that helps users navigate through your system by providing clear step-by-step guidance.

## Features

- Uses OpenAI API for natural language understanding
- Dynamically generates navigation instructions based on JSON site structure
- RESTful API with FastAPI
- Friendly, conversational responses to user questions

## Project Structure

```
app/
├── services/
│   └── helper_bot/
│       ├── helper_bot.py       # Bot implementation
│       ├── helper_bot_router.py # FastAPI router
│       └── helper_bot_schema.py # Pydantic models
├── config/
│   └── config.py               # Configuration and settings
├── main.py                     # FastAPI application
├── .env                        # Environment variables
├── .gitignore                  # Git ignore file
├── data.json                   # Site structure data
├── README.md                   # This file
└── requirements.txt            # Project dependencies
```

## Installation and Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your environment variables in `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_ENDPOINT=https://api.openai.com/v1/chat/completions
   MODEL=gpt-3.5-turbo
   ```
4. Update the `data.json` file with your site structure

## Running the Application

```
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

- `GET /`: Welcome message
- `GET /health`: Health check
- `POST /helper-bot/chat`: Chat with the helper bot
- `GET /helper-bot/health`: Helper bot service health check
- `GET /docs`: Swagger documentation

## Usage Example

```bash
curl -X POST "http://localhost:8000/helper-bot/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I change my profile picture?", "history": []}'
```

Response:
```json
{
  "response": "To change your profile picture, follow these steps:\n\nGo to User Account → Profile → Avatar Settings\n\nClick on your current avatar, then select 'Upload new image'. Choose an image file from your device, adjust the crop area if needed, and click 'Save'.",
  "path": ["user", "profile", "avatar"]
}
```

## Customization

Update the `data.json` file to match your system's structure. Each node can include:

- `title`: Display name of the section
- `description`: Brief description
- `instructions`: Specific user instructions
- `actions`: Available action buttons
- `fields`: Form fields (if applicable)
- `keywords`: Search keywords to match user queries