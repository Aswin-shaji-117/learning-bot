# Document-Based Subject Chatbot Using RAG

A FastAPI-based chatbot application that uses Retrieval Augmented Generation (RAG) to answer questions based on uploaded documents. Documents are organized by subjects, and the chatbot provides answers strictly based on the document content.

## Features

- **Subject Management**: Create and manage different subjects (e.g., HR, Finance, Product Docs)
- **Document Upload**: Upload PDF and TXT files to specific subjects
- **Intelligent Chunking**: Automatically chunks documents for optimal retrieval
- **Vector Search**: Uses ChromaDB for efficient semantic search
- **RAG Chatbot**: Answers questions based only on subject-specific documents
- **Open-Source Models**: Uses Sentence Transformers for embeddings and Flan-T5 for generation

## Technology Stack

- **Framework**: FastAPI
- **Vector Database**: ChromaDB
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **LLM**: google/flan-t5-base (open-source)
- **Document Processing**: PyPDF2

## RAG Implementation Details

### 1. RAG Approach
This implementation uses a classic RAG pipeline: documents are split into 500-character chunks with 50-character overlap, converted to embeddings using Sentence Transformers, and stored in ChromaDB. When a user asks a question, we retrieve the top 5 most semantically similar chunks using cosine similarity, then pass them as context to Flan-T5 to generate grounded answers.

### 2. Embedding Model Choice
We chose **all-MiniLM-L6-v2** because it offers an excellent balance of performance and accuracy. At only 80MB, it's lightweight and fast (384-dimensional embeddings), making it ideal for real-time queries while still providing high-quality semantic search. It's also completely free and runs locally without API costs.

### 3. Chunking Strategy
- **Chunk Size**: 500 characters - large enough to preserve context but small enough for precise retrieval
- **Overlap**: 50 characters - prevents information loss at chunk boundaries
- **Similarity Metric**: Cosine similarity (default in ChromaDB) - works well with normalized embeddings from Sentence Transformers

### 4. Hallucination Prevention
- **Strict Retrieval-Only**: The LLM only receives retrieved document chunks as context, no external knowledge
- **Explicit Checks**: If no relevant documents are found (empty retrieval), the system returns "No information found in the subject documents"
- **Source Attribution**: Every answer includes source filenames, allowing verification
- **Subject Isolation**: Each subject has its own vector collection, preventing cross-contamination

### 5. Future Improvements
- **Hybrid Search**: Combine semantic search with keyword-based BM25 for better recall
- **Larger LLM**: Upgrade to Flan-T5-Large or LLaMA for better answer quality
- **Caching**: Implement Redis caching for frequently asked questions
- **Evaluation**: Add RAGAS metrics to measure retrieval and generation quality

## Project Structure

```
chat-bot/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration settings
├── schemas.py              # Pydantic models
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── routers/
│   ├── subjects.py        # Subject management endpoints
│   ├── documents.py       # Document upload endpoints
│   └── chat.py            # Chatbot endpoints
├── services/
│   ├── subject_service.py    # Subject business logic
│   ├── vector_db_service.py  # ChromaDB operations
│   └── chatbot_service.py    # RAG chatbot logic
└── utils/
    └── document_processor.py # Document extraction and chunking
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Setup Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd d:\AI-Agents\chat-bot
   ```

2. **Create a virtual environment**:
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

5. **Create environment file**:
   ```powershell
   copy .env.example .env
   ```

6. **Run the application**:
   ```powershell
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Create Subject

**POST** `/subjects/`

Create a new subject to organize documents.

```json
{
  "name": "HR Policies",
  "description": "Human Resources policies and guidelines"
}
```

**Response**:
```json
{
  "id": "uuid-string",
  "name": "HR Policies",
  "description": "Human Resources policies and guidelines",
  "created_at": "2025-12-12T10:00:00",
  "document_count": 0
}
```

### 2. List All Subjects

**GET** `/subjects/`

Get a list of all subjects.

**Response**:
```json
[
  {
    "id": "uuid-string",
    "name": "HR Policies",
    "description": "Human Resources policies and guidelines",
    "created_at": "2025-12-12T10:00:00",
    "document_count": 2
  }
]
```

### 3. Get Subject by ID

**GET** `/subjects/{subject_id}`

Get details of a specific subject.

### 4. Delete Subject

**DELETE** `/subjects/{subject_id}`

Delete a subject and all its documents.

### 5. Upload Document

**POST** `/documents/upload`

Upload a PDF or TXT file to a subject.

**Form Data**:
- `subject_id`: ID of the subject
- `file`: PDF or TXT file

**Response**:
```json
{
  "document_id": "uuid-string",
  "subject_id": "uuid-string",
  "filename": "policy.pdf",
  "file_type": "pdf",
  "chunks_created": 25,
  "message": "Document uploaded and processed successfully"
}
```

### 6. Ask Question (Chat)

**POST** `/chat/`

Ask a question to the subject chatbot.

```json
{
  "subject_id": "uuid-string",
  "question": "What is the vacation policy?"
}
```

**Response**:
```json
{
  "subject_id": "uuid-string",
  "question": "What is the vacation policy?",
  "answer": "According to the documents, employees are entitled to 15 days of paid vacation per year...",
  "sources": ["policy.pdf", "guidelines.txt"]
}
```

If no relevant information is found:
```json
{
  "subject_id": "uuid-string",
  "question": "What is the dress code?",
  "answer": "No information found in the subject documents.",
  "sources": []
}
```

## Usage Example

### Using cURL

1. **Create a subject**:
```bash
curl -X POST "http://localhost:8000/subjects/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Finance", "description": "Financial policies"}'
```

2. **Upload a document**:
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "subject_id=your-subject-id" \
  -F "file=@path/to/document.pdf"
```

3. **Ask a question**:
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"subject_id": "your-subject-id", "question": "What are the expense guidelines?"}'
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Create subject
response = requests.post(
    f"{BASE_URL}/subjects/",
    json={"name": "HR", "description": "HR documents"}
)
subject = response.json()
subject_id = subject["id"]

# Upload document
with open("policy.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/documents/upload",
        data={"subject_id": subject_id},
        files={"file": f}
    )
print(response.json())

# Ask question
response = requests.post(
    f"{BASE_URL}/chat/",
    json={
        "subject_id": subject_id,
        "question": "What is the vacation policy?"
    }
)
print(response.json()["answer"])
```

## Configuration

Edit the `.env` file to customize:


- `LLM_MODEL`: HuggingFace model for text generation (default: google/flan-t5-base)
- `CHUNK_SIZE`: Size of text chunks (default: 500)
- `EMBEDDING_MODEL`: Sentence transformer model for embeddings (default: all-MiniLM-L6-v2)
- `LLM_MODEL`: HuggingFace model for text generation (default: google/flan-t5-base)
- `CHUNK_SIZE`: Size of text chunks (default: 500)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)
- `MAX_FILE_SIZE_MB`: Maximum file upload size (default: 10)

## Models Used

### Embedding Model
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Purpose**: Converts text to vector embeddings
- **Dimensions**: 384
- **Size**: ~80MB
- **Performance**: Fast and efficient for semantic search
- **Cost**: Free (runs locally)

### LLM Model
- **Model**: google/flan-t5-base
- **Purpose**: Generates answers based on retrieved context
- **Size**: ~250MB
- **Performance**: Good balance between quality and speed
- **Cost**: Free (runs locally)

> **Note**: Both models are downloaded automatically on first run. You can change them in the `.env` file to other open-source alternatives like `google/flan-t5-large` for better quality or `google/flan-t5-small` for faster responses.

## Configuration

Edit the `.env` file to customize:

- `EMBEDDING_MODEL`: Sentence transformer model for embeddings (default: all-MiniLM-L6-v2)
- `LLM_MODEL`: HuggingFace model for text generation (default: google/flan-t5-base)
- `CHUNK_SIZE`: Size of text chunks (default: 500)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)
- `MAX_FILE_SIZE_MB`: Maximum file upload size (default: 10)

## Troubleshooting

### Issue: Models downloading slowly
**Solution**: Both models are downloaded from HuggingFace on first run. Ensure you have a stable internet connection.

### Issue: Out of memory errors
**Solution**: Use smaller models in `.env`:
```
EMBEDDING_MODEL=sentence-transformers/paraphrase-MiniLM-L3-v2
LLM_MODEL=google/flan-t5-small
```

### Issue: Poor answer quality
**Solution**: Try a larger LLM model or increase chunk size:
```
LLM_MODEL=google/flan-t5-large
CHUNK_SIZE=1000
```

## License

MIT License - Feel free to use and modify as needed.

## Support

For issues and questions, please refer to the API documentation at `/docs` when the server is running.
