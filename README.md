# Backend API with SQLite

A Flask-based backend API with RAG (Retrieval-Augmented Generation) capabilities using SQLite database.

## Features

- RESTful API with Flask
- SQLite database with SQLAlchemy ORM
- Database migrations with Flask-Migrate
- RAG implementation with embeddings
- Chat service with conversation history
- Health check endpoints

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Initialize Database

```bash
python -c "from app.db.init_db import init_database; init_database()"
```

### 4. Run Migrations

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Run Application

```bash
python app/main.py
```

Or with Gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 app.main:app
```

## API Endpoints

### Health Check
- `GET /api/health` - Check API status

### Chat
- `POST /api/chat` - Send a chat message
  ```json
  {
    "message": "Hello",
    "user_id": "user123",
    "conversation_id": "conv456"
  }
  ```

### Greetings
- `GET /api/greetings` - Get all greetings
- `POST /api/greetings` - Create a new greeting

## Project Structure

```
backend/
├── app/
│   ├── api/          # API routes
│   ├── models/       # Database models
│   ├── services/     # Business logic
│   ├── rag/          # RAG implementation
│   ├── schemas/      # Request/response schemas
│   ├── db/           # Database configuration
│   └── utils/        # Utility functions
├── instance/         # SQLite database files
├── tests/            # Unit tests
└── requirements.txt
```

## Testing

```bash
pytest tests/
```

## Docker

### Build

```bash
docker build -t backend-api .
```

### Run

```bash
docker run -p 5000:5000 backend-api
```

## License

MIT