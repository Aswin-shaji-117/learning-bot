import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import uuid
from config import settings


class VectorDBService:
    """Service for managing ChromaDB operations and embeddings"""
    
    def __init__(self):
        """Initialize ChromaDB client and embedding model"""
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        print(f"Embedding model loaded successfully")
        
    def get_or_create_collection(self, subject_id: str):
        """
        Get or create a collection for a subject
        
        Args:
            subject_id: Unique identifier for the subject
            
        Returns:
            ChromaDB collection
        """
        collection_name = f"subject_{subject_id}"
        return self.client.get_or_create_collection(name=collection_name)
    
    def add_documents(
        self,
        subject_id: str,
        document_id: str,
        chunks: List[str],
        metadata: Dict
    ) -> int:
        """
        Add document chunks to the vector database
        
        Args:
            subject_id: Subject identifier
            document_id: Document identifier
            chunks: List of text chunks
            metadata: Metadata about the document
            
        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0
        
        collection = self.get_or_create_collection(subject_id)
        
        # Generate embeddings using sentence-transformers
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        # Create unique IDs for each chunk
        chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Create metadata for each chunk
        metadatas = [
            {
                **metadata,
                "chunk_index": i,
                "document_id": document_id
            }
            for i in range(len(chunks))
        ]
        
        # Add to collection
        collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=chunk_ids
        )
        
        return len(chunks)
    
    def query_documents(
        self,
        subject_id: str,
        query: str,
        n_results: int = 5
    ) -> Dict:
        """
        Query documents in a subject's collection
        
        Args:
            subject_id: Subject identifier
            query: Query text
            n_results: Number of results to return
            
        Returns:
            Query results with documents and metadata
        """
        try:
            collection = self.get_or_create_collection(subject_id)
            
            # Check if collection has any documents
            if collection.count() == 0:
                return {
                    "documents": [],
                    "metadatas": [],
                    "distances": []
                }
            
            # Generate query embedding using sentence-transformers
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Query the collection
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=min(n_results, collection.count())
            )
            
            return {
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else []
            }
        except Exception as e:
            print(f"Error querying documents: {str(e)}")
            return {
                "documents": [],
                "metadatas": [],
                "distances": []
            }
    
    def delete_collection(self, subject_id: str):
        """
        Delete a subject's collection
        
        Args:
            subject_id: Subject identifier
        """
        collection_name = f"subject_{subject_id}"
        try:
            self.client.delete_collection(name=collection_name)
        except Exception:
            pass  # Collection might not exist
    
    def get_collection_count(self, subject_id: str) -> int:
        """
        Get the number of documents in a collection
        
        Args:
            subject_id: Subject identifier
            
        Returns:
            Count of documents
        """
        try:
            collection = self.get_or_create_collection(subject_id)
            return collection.count()
        except Exception:
            return 0


# Singleton instance
vector_db_service = VectorDBService()
