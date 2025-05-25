# 💡 Idea Symphony 🎵

Idea Symphony is an AI-powered brainstorming application that helps users develop and refine their ideas through structured, multi-participant brainstorming sessions. The application uses multiple AI models to generate questions, facilitate brainstorming, and synthesize results.

## Architecture

The application is split into two main components:

- **Backend**: A FastAPI service that handles the core brainstorming logic and AI model interactions
- **Frontend**: A Streamlit application that provides the user interface

## Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)
- A Logfire account and API token (for logging)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
LOGFIRE_TOKEN=your_logfire_token_here
```

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd idea-symphony
```

2. Create a `.env` file with your Logfire token (see Environment Variables above)

3. Start the application using Docker Compose:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development Setup

### Backend Development

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Run the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Development

1. Create a virtual environment (if not already done):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install frontend dependencies:
```bash
cd frontend
pip install -r requirements.txt
```

3. Run the Streamlit app:
```bash
streamlit run app/app.py
```

## Project Structure
```
idea-symphony/
├── backend/
│ ├── app/
│ │ ├── main.py # FastAPI application and endpoints
│ │ ├── models.py # Pydantic models
│ │ └── idea_symphony.py # Core brainstorming logic
│ ├── Dockerfile
│ └── requirements.txt
├── frontend/
│ ├── app/
│ │ ├── app.py # Streamlit UI
│ │ └── client.py # API client
│ ├── Dockerfile
│ └── requirements.txt
├── docker-compose.yml
└── .env
```

## API Endpoints

The backend provides the following endpoints:

- `POST /api/create-context`: Create a context document from user input
- `POST /api/generate-questions`: Generate brainstorming questions
- `POST /api/synthesize-questions`: Synthesize multiple question sets
- `POST /api/chunk-questions`: Group questions by topic
- `POST /api/brainstorm`: Generate brainstorming responses
- `POST /api/synthesize`: Synthesize all brainstorming responses

For detailed API documentation, visit http://localhost:8000/docs when the backend is running.

## Features

- **Multi-Model Question Generation**: Generate diverse brainstorming questions using multiple AI models
- **Structured Brainstorming**: Organize questions by topic and generate detailed responses
- **Human-AI Collaboration**: Option to include human participants in the brainstorming process
- **Response Synthesis**: Automatically synthesize and organize brainstorming responses
- **Export Options**: Download results in both attributed and non-attributed formats

## Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure the backend is running (`docker-compose ps`)
   - Check the backend logs (`docker-compose logs backend`)
   - Verify the backend URL in the frontend client

2. **Logfire Token Issues**
   - Verify your Logfire token in the `.env` file
   - Check the backend logs for authentication errors

3. **Docker Issues**
   - Ensure Docker and Docker Compose are running
   - Try rebuilding the containers: `docker-compose up --build --force-recreate`

### Logs

View logs for specific services:
```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# All logs
docker-compose logs
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Support

For support, please [create an issue](https://github.com/matthannigan/idea-symphony_prototype/issues) or contact [Matt Hannigan](https://github.com/matthannigan).

