import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid
from typing import List
import re

class RAGService:
    def __init__(self):
        # Initialize ChromaDB
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        # Clean the text
        text = re.sub(r'\s+', ' ', text.strip())
        
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
        
        return chunks
    
    def index_document(self, doc_id: int, text: str):
        """Index a document by splitting into chunks and storing embeddings"""
        chunks = self.chunk_text(text)
        
        # Create unique IDs for each chunk
        chunk_ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Create metadata for each chunk
        metadatas = [{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]
        
        # Add chunks to collection
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=chunk_ids
        )
    
    def search(self, query: str, k: int = 5) -> List[str]:
        """Search for relevant chunks using similarity search"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
            
            if results['documents']:
                return results['documents'][0]
            else:
                return []
        
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def delete_document(self, doc_id: int):
        """Delete all chunks for a specific document"""
        # Get all chunk IDs for this document
        results = self.collection.get(
            where={"doc_id": doc_id}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
    
    def get_document_chunks(self, doc_id: int) -> List[str]:
        """Get all chunks for a specific document"""
        results = self.collection.get(
            where={"doc_id": doc_id}
        )
        
        if results['documents']:
            # Sort by chunk index
            chunks_with_metadata = list(zip(results['documents'], results['metadatas']))
            chunks_with_metadata.sort(key=lambda x: x[1]['chunk_index'])
            return [chunk for chunk, _ in chunks_with_metadata]
        
        return []