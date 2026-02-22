"""
Document Loader - Loads files from knowledge_base/documents/
Supports: .txt, .md, .pdf, .docx
"""
import os
from typing import List, Dict
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentLoader:
    """Load documents from various file formats"""
    
    def __init__(self, knowledge_base_path: str = None):
        """Initialize loader"""
        self.knowledge_base_path = knowledge_base_path or os.getenv(
            'KNOWLEDGE_BASE_PATH', 
            'knowledge_base/documents'
        )
        self.supported_extensions = ['.txt', '.md', '.pdf', '.docx']
    
    def load_all_documents(self) -> List[Dict]:
        """
        Load all documents from knowledge base
        
        Returns:
            List of document dictionaries with text and metadata
        """
        documents = []
        
        if not os.path.exists(self.knowledge_base_path):
            logger.warning(f"Knowledge base path not found: {self.knowledge_base_path}")
            return documents
        
        for root, dirs, files in os.walk(self.knowledge_base_path):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                if ext in self.supported_extensions:
                    try:
                        doc = self.load_document(file_path)
                        if doc:
                            documents.append(doc)
                    except Exception as e:
                        logger.error(f"Error loading {file_path}: {str(e)}")
        
        logger.info(f"Loaded {len(documents)} documents")
        return documents
    
    def load_document(self, file_path: str) -> Dict:
        """Load a single document"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.txt':
            return self._load_txt(file_path)
        elif ext == '.md':
            return self._load_markdown(file_path)
        elif ext == '.pdf':
            return self._load_pdf(file_path)
        elif ext == '.docx':
            return self._load_docx(file_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return None
    
    def _load_txt(self, file_path: str) -> Dict:
        """Load text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return {
            'text': text,
            'metadata': {
                'source': file_path,
                'filename': os.path.basename(file_path),
                'type': 'txt'
            }
        }
    
    def _load_markdown(self, file_path: str) -> Dict:
        """Load markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return {
            'text': text,
            'metadata': {
                'source': file_path,
                'filename': os.path.basename(file_path),
                'type': 'markdown'
            }
        }
    
    def _load_pdf(self, file_path: str) -> Dict:
        """Load PDF file"""
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(file_path)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            
            return {
                'text': text.strip(),
                'metadata': {
                    'source': file_path,
                    'filename': os.path.basename(file_path),
                    'type': 'pdf',
                    'pages': len(reader.pages)
                }
            }
        except ImportError:
            logger.error("pypdf not installed. Install: pip install pypdf")
            return None
        except Exception as e:
            logger.error(f"Error loading PDF: {str(e)}")
            return None
    
    def _load_docx(self, file_path: str) -> Dict:
        """Load Word document"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = "\n\n".join([para.text for para in doc.paragraphs if para.text])
            
            return {
                'text': text,
                'metadata': {
                    'source': file_path,
                    'filename': os.path.basename(file_path),
                    'type': 'docx',
                    'paragraphs': len(doc.paragraphs)
                }
            }
        except ImportError:
            logger.error("python-docx not installed. Install: pip install python-docx")
            return None
        except Exception as e:
            logger.error(f"Error loading DOCX: {str(e)}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 300, chunk_overlap: int = 30) -> List[str]:
        """
        Split text into chunks - MEMORY SAFE VERSION
        
        Args:
            text: Text to chunk
            chunk_size: Max chunk size (default 300 for memory safety)
            chunk_overlap: Overlap between chunks (default 30)
            
        Returns:
            List of text chunks
        """
        # Handle empty or None text
        if not text or len(text.strip()) == 0:
            return []
        
        # For very small text, return as is
        if len(text) <= chunk_size:
            return [text.strip()]
        
        chunks = []
        start = 0
        text_length = len(text)
        
        # SAFETY: Limit total chunks to prevent memory issues
        MAX_CHUNKS = 500  # Maximum 500 chunks per document
        chunk_count = 0
        
        while start < text_length and chunk_count < MAX_CHUNKS:
            # Calculate end position
            end = min(start + chunk_size, text_length)
            
            # Try to break at sentence boundary
            if end < text_length:
                # Look for sentence endings
                for sep in ['. ', '.\n', '! ', '!\n', '? ', '?\n', '\n\n']:
                    pos = text.rfind(sep, start, end)
                    if pos != -1:
                        end = pos + len(sep)
                        break
            
            # Extract chunk
            chunk = text[start:end].strip()
            
            # Only add non-empty chunks
            if chunk and len(chunk) > 10:  # Skip very small chunks
                chunks.append(chunk)
                chunk_count += 1
            
            # Move to next chunk with overlap
            start = end - chunk_overlap
            
            # Prevent infinite loop - if we're not advancing, force move forward
            if start <= 0 or (end - chunk_overlap) <= 0:
                start = end
        
        # Log warning if we hit the limit
        if chunk_count >= MAX_CHUNKS:
            logger.warning(f"Document exceeded {MAX_CHUNKS} chunks, truncated for memory safety")
        
        return chunks
    
    def load_and_chunk_documents(self, chunk_size: int = 300, chunk_overlap: int = 30) -> List[Dict]:
        """
        Load all documents and split into chunks
        MEMORY SAFE: Uses smaller default chunk size
        
        Args:
            chunk_size: Default 300 (reduced from 500 for memory safety)
            chunk_overlap: Default 30 (reduced from 50)
            
        Returns:
            List of chunked documents
        """
        documents = self.load_all_documents()
        chunked_docs = []
        
        logger.info(f"Chunking {len(documents)} documents with size={chunk_size}, overlap={chunk_overlap}")
        
        for doc in documents:
            try:
                chunks = self.chunk_text(doc['text'], chunk_size, chunk_overlap)
                
                for i, chunk in enumerate(chunks):
                    chunked_doc = {
                        'text': chunk,
                        'metadata': {
                            **doc['metadata'],
                            'chunk_index': i,
                            'total_chunks': len(chunks)
                        }
                    }
                    chunked_docs.append(chunked_doc)
                
                logger.info(f"  {doc['metadata']['filename']}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error chunking {doc['metadata']['filename']}: {str(e)}")
                continue
        
        logger.info(f"Created {len(chunked_docs)} chunks from {len(documents)} documents")
        return chunked_docs