from fastapi import APIRouter, HTTPException
from typing import List
from schemas import SubjectCreate, SubjectResponse
from services.subject_service import subject_service

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.post("/", response_model=SubjectResponse, status_code=201)
async def create_subject(subject: SubjectCreate):
    """
    Create a new subject
    
    Args:
        subject: Subject creation data
        
    Returns:
        Created subject
    """
    created_subject = subject_service.create_subject(
        name=subject.name,
        description=subject.description
    )
    
    return SubjectResponse(
        id=created_subject["id"],
        name=created_subject["name"],
        description=created_subject.get("description"),
        created_at=created_subject["created_at"],
        document_count=0
    )


@router.get("/", response_model=List[SubjectResponse])
async def list_subjects():
    """
    List all subjects
    
    Returns:
        List of all subjects
    """
    subjects = subject_service.list_subjects()
    
    return [
        SubjectResponse(
            id=s["id"],
            name=s["name"],
            description=s.get("description"),
            created_at=s["created_at"],
            document_count=len(s.get("documents", []))
        )
        for s in subjects
    ]


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(subject_id: str):
    """
    Get a specific subject by ID
    
    Args:
        subject_id: Subject identifier
        
    Returns:
        Subject details
    """
    subject = subject_service.get_subject(subject_id)
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    return SubjectResponse(
        id=subject["id"],
        name=subject["name"],
        description=subject.get("description"),
        created_at=subject["created_at"],
        document_count=len(subject.get("documents", []))
    )


@router.delete("/{subject_id}", status_code=204)
async def delete_subject(subject_id: str):
    """
    Delete a subject and all its documents
    
    Args:
        subject_id: Subject identifier
    """
    success = subject_service.delete_subject(subject_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    return None
