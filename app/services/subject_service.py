from typing import Dict, List, Optional
import uuid
from datetime import datetime
import json
from pathlib import Path
from config import settings
from services.vector_db_service import vector_db_service


class SubjectService:
    """Service for managing subjects"""
    
    def __init__(self):
        """Initialize subject service"""
        self.subjects_file = Path("subjects.json")
        self._load_subjects()
    
    def _load_subjects(self):
        """Load subjects from file"""
        if self.subjects_file.exists():
            with open(self.subjects_file, 'r') as f:
                self.subjects = json.load(f)
        else:
            self.subjects = {}
    
    def _save_subjects(self):
        """Save subjects to file"""
        with open(self.subjects_file, 'w') as f:
            json.dump(self.subjects, f, indent=2)
    
    def create_subject(self, name: str, description: Optional[str] = None) -> Dict:
        """
        Create a new subject
        
        Args:
            name: Name of the subject
            description: Optional description
            
        Returns:
            Subject data
        """
        subject_id = str(uuid.uuid4())
        
        subject = {
            "id": subject_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "documents": []
        }
        
        self.subjects[subject_id] = subject
        self._save_subjects()
        
        return subject
    
    def get_subject(self, subject_id: str) -> Optional[Dict]:
        """
        Get a subject by ID
        
        Args:
            subject_id: Subject identifier
            
        Returns:
            Subject data or None
        """
        return self.subjects.get(subject_id)
    
    def list_subjects(self) -> List[Dict]:
        """
        List all subjects
        
        Returns:
            List of subjects
        """
        return list(self.subjects.values())
    
    def delete_subject(self, subject_id: str) -> bool:
        """
        Delete a subject and its vector collection
        
        Args:
            subject_id: Subject identifier
            
        Returns:
            True if deleted, False if not found
        """
        if subject_id not in self.subjects:
            return False
        
        # Delete from vector DB
        vector_db_service.delete_collection(subject_id)
        
        # Delete from subjects
        del self.subjects[subject_id]
        self._save_subjects()
        
        return True
    
    def add_document_to_subject(
        self,
        subject_id: str,
        document_id: str,
        filename: str,
        file_type: str
    ) -> bool:
        """
        Add a document reference to a subject
        
        Args:
            subject_id: Subject identifier
            document_id: Document identifier
            filename: Name of the file
            file_type: Type of the file
            
        Returns:
            True if successful
        """
        if subject_id not in self.subjects:
            return False
        
        document = {
            "id": document_id,
            "filename": filename,
            "file_type": file_type,
            "uploaded_at": datetime.now().isoformat()
        }
        
        self.subjects[subject_id]["documents"].append(document)
        self._save_subjects()
        
        return True
    
    def get_document_count(self, subject_id: str) -> int:
        """
        Get the number of documents in a subject
        
        Args:
            subject_id: Subject identifier
            
        Returns:
            Number of documents
        """
        subject = self.subjects.get(subject_id)
        if not subject:
            return 0
        return len(subject.get("documents", []))


# Singleton instance
subject_service = SubjectService()
