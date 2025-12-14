import PyPDF2
from typing import List
import io
from pathlib import Path


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from PDF file content
    
    Args:
        file_content: PDF file content in bytes
        
    Returns:
        Extracted text from the PDF
    """
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")


def extract_text_from_txt(file_content: bytes) -> str:
    """
    Extract text from text file content
    
    Args:
        file_content: Text file content in bytes
        
    Returns:
        Decoded text from the file
    """
    try:
        # Try UTF-8 first, then fall back to other encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                return file_content.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        raise ValueError("Could not decode text file with common encodings")
    except Exception as e:
        raise ValueError(f"Error extracting text from TXT: {str(e)}")


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: The text to chunk
        chunk_size: Maximum size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        # Get the chunk
        end = start + chunk_size
        chunk = text[start:end]
        
        # If this is not the last chunk and doesn't end at the text boundary,
        # try to break at a sentence or word boundary
        if end < text_length:
            # Look for sentence ending
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            last_break = max(last_period, last_newline)
            
            if last_break > chunk_size * 0.5:  # Only break if we're past halfway
                end = start + last_break + 1
                chunk = text[start:end]
        
        # Add the chunk if it has content
        if chunk.strip():
            chunks.append(chunk.strip())
        
        # Move start position (with overlap)
        start = end - chunk_overlap if end < text_length else text_length
    
    return chunks


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension in lowercase
    """
    return Path(filename).suffix.lower()
