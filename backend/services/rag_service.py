import chromadb
from chromadb.config import Settings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
import uuid
from typing import List, Optional
import re
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, chroma_path: str = "./chroma_db", max_retries: int = 3):
        self.chroma_path = chroma_path
        self.max_retries = max_retries
        self.client: Optional[chromadb.PersistentClient] = None
        self.collection = None
        self.embedding_model = None
        self._initialize_chromadb()
        self._initialize_embedding_model()
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB with error handling"""
        try:
            self.client = chromadb.PersistentClient(path=self.chroma_path)
            self.collection = self.client.get_or_create_collection(name="documents")
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise RuntimeError(f"ChromaDB initialization failed: {str(e)}")
    
    def _initialize_embedding_model(self):
        """Initialize embedding model with error handling"""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load embedding model: {e}")
                self.embedding_model = None
        else:
            logger.warning("sentence-transformers not available. RAG features will be limited.")
            self.embedding_model = None
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
        
        # Clean the text
        text = re.sub(r'\s+', ' ', text.strip())
        logger.info(f"Chunking text of length {len(text)} with chunk_size={chunk_size}, overlap={overlap}")
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end != -1 and sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def index_document(self, doc_id: int, text: str):
        """Index a document by splitting into chunks and storing embeddings"""
        if not self.collection:
            logger.error("ChromaDB collection not initialized")
            raise RuntimeError("RAG service not properly initialized")
        
        try:
            chunks = self.chunk_text(text)
            if not chunks:
                logger.warning(f"No chunks created for document {doc_id}")
                return
            
            # Create unique IDs for each chunk
            chunk_ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]
            
            # Create metadata for each chunk
            metadatas = [{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]
            
            # Add chunks to collection with retries
            for attempt in range(self.max_retries):
                try:
                    self.collection.add(
                        documents=chunks,
                        metadatas=metadatas,
                        ids=chunk_ids
                    )
                    logger.info(f"Successfully indexed document {doc_id} with {len(chunks)} chunks")
                    return
                except Exception as e:
                    logger.warning(f"Indexing attempt {attempt+1} failed: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
            
            logger.error(f"Failed to index document {doc_id} after {self.max_retries} attempts")
            raise RuntimeError(f"Failed to index document {doc_id}")
        
        except Exception as e:
            logger.error(f"Error indexing document {doc_id}: {e}")
            raise
    
    def search(self, query: str, k: int = 5) -> List[str]:
        """Search for relevant chunks using similarity search"""
        if not self.collection:
            logger.error("ChromaDB collection not initialized")
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
            
            if results and results.get('documents'):
                chunks = results['documents'][0]
                logger.info(f"Search for '{query}' returned {len(chunks)} chunks")
                return chunks
            else:
                logger.info(f"No results found for query: {query}")
                return []
        
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def delete_document(self, doc_id: int):
        """Delete all chunks for a specific document"""
        if not self.collection:
            logger.error("ChromaDB collection not initialized")
            return
        
        try:
            # Get all chunk IDs for this document
            results = self.collection.get(where={"doc_id": doc_id})
            
            if results and results.get('ids'):
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {doc_id}")
            else:
                logger.warning(f"No chunks found for document {doc_id}")
        
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            raise
    
    def get_document_chunks(self, doc_id: int) -> List[str]:
        """Get all chunks for a specific document"""
        if not self.collection:
            logger.error("ChromaDB collection not initialized")
            return []
        
        try:
            results = self.collection.get(where={"doc_id": doc_id})
            
            if results and results.get('documents'):
                # Sort by chunk index
                chunks_with_metadata = list(zip(results['documents'], results.get('metadatas', [])))
                chunks_with_metadata.sort(key=lambda x: x[1].get('chunk_index', 0) if x[1] else 0)
                chunks = [chunk for chunk, _ in chunks_with_metadata]
                logger.info(f"Retrieved {len(chunks)} chunks for document {doc_id}")
                return chunks
            else:
                logger.warning(f"No chunks found for document {doc_id}")
                return []
        
        except Exception as e:
            logger.error(f"Error retrieving chunks for document {doc_id}: {e}")
            return []