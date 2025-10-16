# Document QA API

A production-ready document-based question answering API using FastAPI, OpenAI embeddings, FAISS vector store, and GPT-4 for answer generation.

## Features

✅ **Core Requirements**
- Document ingestion and indexing with chunking
- Semantic search using OpenAI embeddings and FAISS
- Answer generation using GPT-4
- Document listing and deletion
- RESTful API with FastAPI

✅ **Bonus Features**
- File upload support (PDF, TXT, DOCX, Markdown)
- Streaming support for long LLM responses
- JWT-based authentication
- Asynchronous FastAPI routes
- Interactive web UI

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vector Store**: FAISS
- **LLM**: OpenAI GPT-4-turbo
- **Authentication**: JWT (JSON Web Tokens)

## Prerequisites

- Ubuntu 20.04+ (or compatible Linux distribution)
- Python 3.11+
- OpenAI API key

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd rag-pipeline-assessment/rag-assesment
```

### 2. Set up the environment

```bash
# Make scripts executable and run setup (creates venv and installs deps)
chmod +x setup.sh run.sh
./setup.sh
```

### 3. Configure environment variables

Create or edit the `.env` file and add your credentials:

```
openai_api_key=your_actual_openai_api_key_here
secret_key=any_secure_random_string

# Optional overrides (defaults shown in app/config.py)
# llm_model=gpt-4-turbo-preview
# embedding_model=text-embedding-ada-002
# chunk_size=1000
# chunk_overlap=200
# max_tokens=2000
# temperature=0.7
```

### 4. Run the application

```bash
# Start the server
./run.sh
```

## API Endpoints

### Authentication

#### Login
```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Documents

#### Index Documents (JSON)
```http
POST /documents/
Authorization: Bearer {token}
Content-Type: application/json

{
  "documents": [
    {
      "title": "Introduction to AI",
      "content": "Artificial Intelligence is...",
      "metadata": {}
    }
  ]
}
```

#### Upload Files
```http
POST /documents/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

files: [file1.pdf, file2.txt, file3.docx]
```

#### List Documents
```http
GET /documents/
Authorization: Bearer {token}
```

#### Delete Document
```http
DELETE /documents/{doc_id}
Authorization: Bearer {token}
```

### Query

#### Ask Question
```http
POST /query/
Authorization: Bearer {token}
Content-Type: application/json

{
  "question": "What is artificial intelligence?",
  "top_k": 5,
  "return_sources": true
}
```

Response:
```json
{
  "answer": "Artificial Intelligence is...",
  "sources": [
    {
      "doc_id": "uuid",
      "title": "Introduction to AI",
      "content": "...",
      "score": 0.95
    }
  ],
  "processing_time": 2.5
}
```

#### Streaming Query
```http
POST /query/stream
Authorization: Bearer {token}
Content-Type: application/json

{
  "question": "What is artificial intelligence?",
  "top_k": 5
}
```

### Health Check

```http
GET /health
```

## Web Interface

Access the web UI at: `http://localhost:8000/`

Default credentials:
- Username: `admin`
- Password: `admin123`

## Project Structure

```
rag-assesment/
├── .env                          # Environment variables
├── .gitignore                    # Git ignore file
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── setup.sh                      # Setup script
├── run.sh                        # Run script
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI application
│   ├── config.py                 # Configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py            # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Authentication
│   │   ├── embeddings_service.py # Embeddings
│   │   ├── vector_store.py       # FAISS management
│   │   ├── document_service.py   # Document processing
│   │   └── qa_service.py         # Q&A logic
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── documents.py      # Document endpoints
│   │   │   ├── query.py          # Query endpoints
│   │   │   └── auth.py           # Auth endpoints
│   │   └── dependencies.py       # FastAPI dependencies
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_processor.py     # File processing
│   │   └── text_splitter.py      # Text chunking
│   └── static/
│       └── index.html            # Web UI
├── data/
│   ├── documents/                # Uploaded files
│   └── vector_store/             # FAISS index
└── tests/
    ├── __init__.py
    └── test_api.py               # API tests
```

## Configuration

Edit `.env` file to customize:

- `openai_api_key`: Your OpenAI API key
- `secret_key`: JWT secret key
- `llm_model`: LLM model (default: gpt-4-turbo-preview)
- `embedding_model`: Embedding model (default: text-embedding-ada-002)
- `chunk_size`: Document chunk size (default: 1000)
- `chunk_overlap`: Chunk overlap (default: 200)
- `max_tokens`: Max response tokens (default: 2000)
- `temperature`: LLM temperature (default: 0.7)

## Testing

# Your can run test using command
pytest tests/test_api.py -v

### Using cURL

```bash
# Login
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Index a document
curl -X POST "http://localhost:8000/documents/" \
  -H "Authorization: Bearer {your_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [{
      "title": "Test Doc",
      "content": "This is a test document about AI and machine learning.",
      "metadata": {}
    }]
  }'

# Ask a question
curl -X POST "http://localhost:8000/query/" \
  -H "Authorization: Bearer {your_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this document about?",
    "top_k": 5,
    "return_sources": true
  }'
```

### Using Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/token",
    data={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# Index document
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8000/documents/",
    headers=headers,
    json={
        "documents": [{
            "title": "AI Document",
            "content": "Artificial Intelligence is the simulation of human intelligence...",
            "metadata": {}
        }]
    }
)

# Ask question
response = requests.post(
    "http://localhost:8000/query/",
    headers=headers,
    json={
        "question": "What is AI?",
        "top_k": 5,
        "return_sources": True
    }
)
print(response.json())

## test documents
available in root, you can also add your own. 
```

## Troubleshooting

### OpenAI API Key Error
Make sure your `.env` file contains a valid OpenAI API key.

### FAISS Installation Issues
If FAISS fails to install, try:
```bash
pip install faiss-cpu --no-cache-dir
```

### Permission Denied
Make scripts executable:
```bash
chmod +x setup.sh run.sh
```

### run.sh starts but `python` not found
- Ensure you ran `./setup.sh` to create the virtualenv.
- `run.sh` uses `venv/bin/python` directly and `cd`s into its own directory, so it works even if your shell PATH is different. If it still fails, confirm the venv exists at `rag-assesment/venv/`.

### Server doesn’t start from outside project directory
- Always run `./run.sh` (it changes to the script directory internally). Avoid invoking uvicorn manually from other paths unless you use the full venv python path.

### Port Already in Use
Change the port in `.env`:
```
PORT=8001
```

## Production Deployment

For production:

1. Change default credentials in `.env`
2. Set `DEBUG=False`
3. Use a production WSGI server (Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```
4. Set up HTTPS with nginx
5. Use a proper database for user management
6. Implement rate limiting
7. Add monitoring and logging

## License

MIT License

## Support

For issues and questions, please contact on email