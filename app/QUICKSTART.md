# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### 1. Automated Setup (Recommended)

```bash
cd backend
chmod +x setup.sh
./setup.sh
```

### 2. Manual Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env fileenv
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -c "from app.db.init_db import init_database; init_database()"
```

## Configuration

Edit `.env` file with your settings:

```env
# Flask Configuration
FLASK_APP=app.main:app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///instance/app.db

# API Keys (optional, for AI features)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Server Configuration
HOST=0.0.0.0
PORT=5000
DEBUG=True
```

## Running the Application

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run Flask development server
python app/main.py
```

The API will be available at `http://localhost:5000`

### Production Mode

```bash
# With Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app.main:app
```

## Testing the API

### Health Check

```bash
curl http://localhost:5000/api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "database": "connected",
  "service": "backend-api"
}
```

### Chat Endpoint

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "user_id": "user123"
  }'
```

Response:
```json
{
  "response": "Hello! I'm doing well, thank you! How can I assist you?",
  "conversation_id": "abc123",
  "timestamp": "2024-01-15T10:30:00",
  "context_used": false
}
```

## Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_chat_api.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   ├── rag/             # RAG implementation
│   ├── schemas/         # Request/response validation
│   ├── db/              # Database configuration
│   └── utils/           # Utility functions
├── instance/            # SQLite database (auto-created)
├── tests/               # Unit tests
├── requirements.txt     # Python dependencies
└── .env                 # Configuration (create from .env.example)
```

## Database Management

### Initialize Database

```bash
python -c "from app.db.init_db import init_database; init_database()"
```

### Clear Database (keeps tables)

```bash
python -c "from app.db.init_db import clear_database; clear_database()"
```

### View Database

```bash
# Using SQLite CLI
sqlite3 instance/app.db

# Show tables
.tables

# Show schema
.schema users

# Query data
SELECT * FROM users;

# Exit
.exit
```

## Common Issues

### Issue: ModuleNotFoundError

**Solution**: Make sure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Database locked error

**Solution**: Make sure only one instance of the app is running. If problem persists:
```bash
rm instance/app.db
python -c "from app.db.init_db import init_database; init_database()"
```

### Issue: Port already in use

**Solution**: Change the port in `.env`:
```env
PORT=5001
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t backend-api .
```

### Run Docker Container

```bash
docker run -p 5000:5000 \
  -e OPENAI_API_KEY=your-key \
  -e ANTHROPIC_API_KEY=your-key \
  backend-api
```

### With Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=sqlite:///instance/app.db
    volumes:
      - ./instance:/app/instance
```

Run:
```bash
docker-compose up -d
```

## Next Steps

- Add your API keys to `.env` for AI features
- Customize the RAG knowledge base in `app/rag/retriever.py`
- Add authentication/authorization
- Set up monitoring and logging
- Configure CORS for your frontend
- Deploy to production server

## Support

For issues or questions, please check:
- README.md
- API documentation
- Test files for usage examplespyto