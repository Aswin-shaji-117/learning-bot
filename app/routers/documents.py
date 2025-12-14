from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import uuid
from pathlib import Path
from config import settings
from schemas import DocumentUploadResponse
from services.subject_service import subject_service
from services.vector_db_service import vector_db_service
from utils.document_processor import (
    extract_text_from_pdf,
    extract_text_from_txt,
    chunk_text,
    get_file_extension
)

router = APIRouter(prefix="/documents", tags=["Documents"])


# Create upload directory if it doesn't exist
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    subject_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a document to a subject
    
    Args:
        subject_id: Subject identifier
        file: PDF or TXT file to upload
        
    Returns:
        Upload confirmation with document details
    """
    # Validate subject exists
    subject = subject_service.get_subject(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Validate file type
    file_ext = get_file_extension(file.filename)
    if file_ext not in ['.pdf', '.txt']:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )
    
    # Check file size
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum of {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    try:
        # Extract text based on file type
        if file_ext == '.pdf':
            text = extract_text_from_pdf(content)
        else:  # .txt
            text = extract_text_from_txt(content)
        
        if not text or not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the file"
            )
        
        # Chunk the text
        chunks = chunk_text(
            text,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No valid chunks created from the document"
            )
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Save file
        file_path = UPLOAD_DIR / f"{document_id}_{file.filename}"
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Store in vector database
        metadata = {
            "filename": file.filename,
            "file_type": file_ext[1:],  # Remove the dot
            "subject_id": subject_id
        }
        
        chunks_created = vector_db_service.add_documents(
            subject_id=subject_id,
            document_id=document_id,
            chunks=chunks,
            metadata=metadata
        )
        
        # Add document to subject
        subject_service.add_document_to_subject(
            subject_id=subject_id,
            document_id=document_id,
            filename=file.filename,
            file_type=file_ext[1:]
        )
        
        return DocumentUploadResponse(
            document_id=document_id,
            subject_id=subject_id,
            filename=file.filename,
            file_type=file_ext[1:],
            chunks_created=chunks_created,
            message="Document uploaded and processed successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )
