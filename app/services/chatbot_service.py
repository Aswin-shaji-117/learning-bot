from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from typing import List, Dict
from services.vector_db_service import vector_db_service
from config import settings


class ChatbotService:
    """Service for RAG-based chatbot"""
    
    def __init__(self):
        """Initialize the LLM model"""
        print(f"Loading LLM model: {settings.LLM_MODEL}")
        self.tokenizer = AutoTokenizer.from_pretrained(settings.LLM_MODEL)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(settings.LLM_MODEL)
        
        # Move to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        print(f"Model loaded on device: {self.device}")
    
    def _create_context(self, documents: List[str]) -> str:
        """
        Create context from retrieved documents
        
        Args:
            documents: List of retrieved document chunks
            
        Returns:
            Formatted context string
        """
        if not documents:
            return ""
        
        context = "Context:\n"
        for i, doc in enumerate(documents[:5], 1):  # Limit to top 5 documents
            context += f"{i}. {doc}\n\n"
        
        return context
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using the LLM
        
        Args:
            question: User's question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        if not context:
            return "No information found in the subject documents."
        
        # Create prompt for the model
        prompt = f"""Based on the following context, answer the question. If the context doesn't contain relevant information, say "No information found in the subject documents."

{context}

Question: {question}
Answer:"""
        
        # Tokenize and generate
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=150,
                num_beams=4,
                early_stopping=True,
                temperature=0.7
            )
        
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # If answer is too generic or empty, return no info message
        if not answer or len(answer.strip()) < 3:
            return "No information found in the subject documents."
        
        return answer
    
    def answer_question(
        self,
        subject_id: str,
        question: str,
        n_results: int = 5
    ) -> Dict:
        """
        Answer a question based on subject documents
        
        Args:
            subject_id: Subject identifier
            question: User's question
            n_results: Number of documents to retrieve
            
        Returns:
            Dictionary with answer and sources
        """
        # Retrieve relevant documents
        results = vector_db_service.query_documents(
            subject_id=subject_id,
            query=question,
            n_results=n_results
        )
        
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        
        # Check if we have any documents
        if not documents or len(documents) == 0:
            return {
                "answer": "No information found in the subject documents.",
                "sources": []
            }
        
        # Create context from documents
        context = self._create_context(documents)
        
        # Generate answer
        answer = self._generate_answer(question, context)
        
        # Extract source filenames
        sources = []
        seen_files = set()
        for metadata in metadatas:
            if metadata and "filename" in metadata:
                filename = metadata["filename"]
                if filename not in seen_files:
                    sources.append(filename)
                    seen_files.add(filename)
        
        return {
            "answer": answer,
            "sources": sources
        }


# Singleton instance - will be initialized on first use
_chatbot_service = None

def get_chatbot_service():
    """Get or create chatbot service instance"""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
    return _chatbot_service
