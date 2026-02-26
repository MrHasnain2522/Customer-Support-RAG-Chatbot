# 🤖 Customer Support Chatbot - Backend API

> AI-powered customer support chatbot backend with RAG (Retrieval Augmented Generation) technology for intelligent, context-aware responses.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-orange.svg)](https://openai.com/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20DB-red.svg)](https://github.com/facebookresearch/faiss)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [RAG System](#-rag-system)
- [Database Schema](#-database-schema)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## ✨ Features

- 🤖 **RAG Technology** - Retrieval Augmented Generation for accurate responses
- 🔍 **Semantic Search** - FAISS vector database for intelligent product search
- 💬 **Conversation Memory** - Context-aware chat with history tracking
- 📊 **Source Attribution** - Automatic citation with deduplication
- 🗄️ **PostgreSQL Database** - Robust data storage with JSONB
- 🔐 **RESTful API** - Clean, documented endpoints
- ⚡ **Local Embeddings** - Fast inference with Sentence Transformers
- 🐳 **Docker Ready** - Containerized deployment
- 📝 **Professional Responses** - Natural, conversational AI tone
- 🎯 **High Accuracy** - Configurable relevance thresholds

---

## 🏗️ Architecture
```
┌──────────────┐
│   Frontend   │
│   (React)    │
└──────┬───────┘
       │ REST API
       ▼
┌──────────────┐      ┌──────────────┐
│  Flask API   │─────▶│  PostgreSQL  │
│              │      │   Database   │
└──────┬───────┘      └──────────────┘
       │
       ├─────────────┐
       ▼             ▼
┌─────────────┐ ┌─────────────┐
│  OpenAI     │ │   FAISS     │
│  GPT-3.5    │ │  Vector DB  │
└─────────────┘ └─────────────┘
       │             │
       └──────┬──────┘
              ▼
      ┌───────────────┐
      │  Knowledge    │
      │     Base      │
      │   (PDFs)      │
      └───────────────┘
```

---

## 🛠️ Tech Stack

### **Backend Framework:**
- Flask 2.3
- SQLAlchemy 2.0
- Flask-CORS

### **AI/ML:**
- OpenAI API (GPT-3.5-turbo)
- FAISS (Vector similarity search)
- Sentence Transformers (all-MiniLM-L6-v2)

### **Database:**
- PostgreSQL 15
- JSONB storage

### **Document Processing:**
- PyPDF2
- NumPy

---

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- OpenAI API Key
- 4GB RAM (8GB recommended)

---

## 🚀 Installation

### **1. Clone Repository**
```bash
git clone https://github.com/MrHasnain2522/Customer-Support-RAG-Chatbot
cd Customer-Support-RAG-Chatbot
```

### **2. Create Virtual Environment**

**Windows:**
```bash
python -m venv env
env\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Set Up Database**
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE rag_chatbot;

--see result in pgadmin
SELECT 
    conversation_id,
    user_id,
    title,
    jsonb_pretty(messages_json) as messages,
    created_at
FROM conversations
ORDER BY created_at DESC;

-- Exit
\q
```

### **5. Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

### **6. Initialize Database**
```bash
python -c "from app import db; db.create_all()"
```

### **7. Add Knowledge Base**
```bash
# Place PDF files in:
knowledge_base/documents/

# Example:
cp your-catalog.pdf knowledge_base/documents/
```

---

## ⚙️ Configuration

### **Environment Variables (.env)**
```env
# Flask
FLASK_APP=app.main:app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/rag_chatbot

# OpenAI
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7

# Embeddings
USE_HUGGINGFACE_API=False
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector Database
VECTOR_DB_TYPE=faiss
FAISS_INDEX_PATH=vector_stores/faiss/index.faiss
FAISS_METADATA_PATH=vector_stores/faiss/metadata.pkl

# RAG Settings
KNOWLEDGE_BASE_PATH=knowledge_base/documents
CHUNK_SIZE=300
CHUNK_OVERLAP=30
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.1
MAX_SOURCES_DISPLAY=3

# Server
HOST=0.0.0.0
PORT=5000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:80
```

---

## 🏃 Running the Application

### **Development Mode**
```bash
# Activate environment
source env/bin/activate  # macOS/Linux
env\Scripts\activate     # Windows

# Run server
python app/main.py
```

Server runs at: `http://localhost:5000`

### **Production Mode**
```bash
# Using Gunicorn (Linux/macOS)
gunicorn -w 4 -b 0.0.0.0:5000 app.main:app

# Using Waitress (Windows)
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app.main:app
```

### **Docker**
```bash
# Build image
docker build -t customer-support-backend .

# Run container
docker run -d -p 5000:5000 --env-file .env customer-support-backend
```

### **Docker Compose**
```bash
# Start all services
docker-compose up -d

# Stop services
docker-compose down
```

---

## 📚 API Documentation

### **Base URL:** `http://localhost:5000/api`

---

### **1. Health Check**
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-24T10:30:00Z"
}
```

---

### **2. Send Message**
```http
POST /api/chat
```

**Request:**
```json
{
  "message": "Do you have black lawn suits?",
  "user_id": "user_123",
  "conversation_id": "conv_abc"  // Optional
}
```

**Response:**
```json
{
  "response": "Yes! We have Black Sophistication lawn suits...",
  "conversation_id": "conv_abc",
  "timestamp": "2026-02-24T10:30:15Z",
  "context_used": true,
  "sources": [
    {
      "filename": "catalog.pdf",
      "relevance": 0.41
    }
  ]
}
```

---

### **3. Get Conversation History**
```http
GET /api/conversations/{conversation_id}
```

**Response:**
```json
{
  "conversation_id": "conv_abc",
  "user_id": "user_123",
  "title": "Do you have black lawn suits?",
  "messages": [...],
  "created_at": "2026-02-24T10:30:00Z"
}
```

---

### **4. Get User Conversations**
```http
GET /api/conversations/user/{user_id}
```

---

### **5. Knowledge Base Stats**
```http
GET /api/knowledge-base/stats
```

**Response:**
```json
{
  "total_documents": 500,
  "dimension": 384,
  "index_type": "IndexFlatL2"
}
```

---

### **6. Reload Knowledge Base**
```http
POST /api/knowledge-base/reload
```

**Request:**
```json
{
  "force": true
}
```

---

## 📁 Project Structure
```
customer-support-chatbot-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── user.py
│   │   └── conversation.py
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── document_loader.py
│   │   ├── faiss_store.py
│   │   ├── retriever.py
│   │   └── generator.py
│   ├── routes/
│   │   ├── chat.py
│   │   ├── conversation.py
│   │   └── knowledge_base.py
│   ├── services/
│   │   └── chat_service.py
│   └── utils/
│       └── logger.py
├── knowledge_base/
│   └── documents/          # Place PDFs here
├── vector_stores/
│   └── faiss/
│       ├── index.faiss
│       └── metadata.pkl
├── .env
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🧠 RAG System

### **How It Works:**

1. **Document Ingestion**
   - Load PDFs from `knowledge_base/documents/`
   - Split into 300-token chunks (30 overlap)
   - Generate embeddings (Sentence Transformers)
   - Store in FAISS vector database

2. **Query Processing**
   - Generate query embedding
   - Semantic search in FAISS (top-k=5)
   - Retrieve relevant documents

3. **Response Generation**
   - Build context from documents
   - Add conversation history
   - Send to OpenAI GPT-3.5
   - Generate natural response
   - Add source citations (deduplicated)

4. **Storage**
   - Save to PostgreSQL with JSONB
   - Track sources and metadata

---

## 🗄️ Database Schema

### **Users Table**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **Conversations Table**
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) REFERENCES users(user_id),
    title VARCHAR(500),
    messages_json JSONB DEFAULT '[]',
    metadata_json JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🚀 Deployment

### **Docker Deployment**
```bash
# Build
docker build -t customer-support-backend .

# Run
docker run -d \
  -p 5000:5000 \
  --env-file .env \
  --name support-api \
  customer-support-backend
```

### **Cloud Deployment**

**Heroku:**
```bash
heroku create customer-support-api
git push heroku main
```

**AWS:**
```bash
eb init -p python-3.11 customer-support-api
eb create support-env
eb deploy
```

---

## 🐛 Troubleshooting

### **FAISS Returns 0 Documents**
```env
# Lower threshold in .env
SIMILARITY_THRESHOLD=0.1
```

### **OpenAI API Error**
```bash
# Update OpenAI library
pip install --upgrade openai
```

### **Port Already in Use**
```bash
# Kill process
lsof -i :5000
kill -9 <PID>
```

### **Memory Error**
```env
# Reduce chunk size
CHUNK_SIZE=200
CHUNK_OVERLAP=20
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 👥 Contact

- **Email:** adsab2522@gmail.com
- **Phone:** 0320-1007448

---

## 🔗 Related Repositories

- **Frontend:** [customer-support-chatbot-frontend](https://github.com/yourusername/customer-support-chatbot-frontend)
- **Chatbot_bakcend:** [customer-support](https://github.com/MrHasnain2522/Customer-Support-RAG-Chatbot)

---

