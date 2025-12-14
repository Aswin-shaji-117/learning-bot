from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
from config import settings
from routers import subjects, documents, chat


# Create necessary directories
Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
Path(settings.CHROMA_PERSIST_DIRECTORY).mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Embedding Model: {settings.EMBEDDING_MODEL}")
    print(f"LLM Model: {settings.LLM_MODEL}")
    
    yield
    
    # Shutdown
    print("Shutting down application...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Document-Based Subject Chatbot using RAG (Retrieval Augmented Generation)",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(subjects.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Document-Based Subject Chatbot using RAG",
        "endpoints": {
            "subjects": "/subjects",
            "documents": "/documents",
            "chat": "/chat",
            "docs": "/docs"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
