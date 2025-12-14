from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SubjectCreate(BaseModel):
    """Schema for creating a new subject"""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the subject")
    description: Optional[str] = Field(None, max_length=500, description="Description of the subject")


class SubjectResponse(BaseModel):
    """Schema for subject response"""
    id: str
    name: str
    description: Optional[str]
    created_at: str
    document_count: int = 0


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""
    document_id: str
    subject_id: str
    filename: str
    file_type: str
    chunks_created: int
    message: str


class ChatRequest(BaseModel):
    """Schema for chat request"""
    subject_id: str = Field(..., description="ID of the subject to query")
    question: str = Field(..., min_length=1, description="Question to ask")


class ChatResponse(BaseModel):
    """Schema for chat response"""
    subject_id: str
    question: str
    answer: str
    sources: Optional[List[str]] = []
