from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import logging
import time
import re
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from database import SessionLocal, engine
from models import Base, Document
from services.pdf_processor import PDFProcessor
try:
    from services.llm_service import LLMService
    from services.rag_service import RAGService
    SERVICES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some services could not be imported: {e}")
    SERVICES_AVAILABLE = False
from schemas import DocumentResponse, DocumentStatus, ProcessingRequest, SummaryResponse

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure FastAPI with larger file upload limits
app = FastAPI(
    title="Dartos - Agentic Info Services", 
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# Mount static files from React build (if available)
static_dir = Path("frontend/build/static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    logger.warning("Frontend build static directory not found, skipping static file mount")

# Initialize services
pdf_processor = PDFProcessor()
if SERVICES_AVAILABLE:
    llm_service = LLMService()
    rag_service = RAGService()
else:
    llm_service = None
    rag_service = None

# Constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'.pdf'}
UPLOAD_DIR = Path("uploads")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Check content type
    if file.content_type and not file.content_type.startswith('application/pdf'):
        raise HTTPException(status_code=400, detail="Invalid content type. Must be PDF.")

def _validate_extracted_text(text: str) -> dict:
    """Validate the quality of extracted text"""
    if not text or not text.strip():
        return {'is_valid': False, 'reason': 'No text content'}
    
    text = text.strip()
    length = len(text)
    
    # Check minimum length
    if length < 50:
        return {'is_valid': False, 'reason': f'Text too short ({length} characters)'}
    
    # Check for excessive special characters (might indicate OCR failure)
    special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace() and c not in '.,!?;:-()[]{}')
    special_ratio = special_chars / length
    
    if special_ratio > 0.3:  # More than 30% special characters
        return {'is_valid': False, 'reason': f'Too many special characters ({special_ratio:.2%}) - possible OCR failure'}
    
    # Check for repetitive characters (might indicate extraction issues)
    if re.search(r'(.)\1{10,}', text):  # 10+ consecutive same characters
        return {'is_valid': False, 'reason': 'Repetitive characters detected - possible extraction error'}
    
    # Check word count
    words = text.split()
    if len(words) < 10:
        return {'is_valid': False, 'reason': f'Insufficient word count ({len(words)} words)'}
    
    return {'is_valid': True, 'reason': 'Text validation passed'}

def save_uploaded_file(file: UploadFile, filename: str) -> str:
    """Save uploaded file to disk"""
    UPLOAD_DIR.mkdir(exist_ok=True)
    file_path = UPLOAD_DIR / filename
    
    try:
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail=f"File too large. Maximum size: {MAX_FILE_SIZE} bytes")
            buffer.write(content)
        logger.info(f"File saved: {file_path}")
        return str(file_path)
    except Exception as e:
        logger.error(f"Failed to save file {filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")

def process_and_index_document(doc_id: int, file_path: str):
    """Background task to process and index document"""
    import time
    start_time = time.time()
    logger.info(f"Starting background processing for document {doc_id} at {time.strftime('%H:%M:%S')}")
    
    db = SessionLocal()
    try:
        
        # Update status to processing
        document = db.query(Document).filter(Document.id == doc_id).first()
        if not document:
            logger.error(f"Document {doc_id} not found")
            return
        
        document.status = "processing"
        db.commit()
        
        # Extract text
        try:
            text_content = pdf_processor.extract_text(file_path)
            
            # Validate extracted text
            validation_result = _validate_extracted_text(text_content)
            if not validation_result['is_valid']:
                logger.warning(f"Text validation failed for document {doc_id}: {validation_result['reason']}")
                document.status = "failed"
                document.error_message = f"Text extraction validation failed: {validation_result['reason']}"
                db.commit()
                return
            
            if not text_content.strip():
                logger.warning(f"No text extracted from {file_path}")
                document.status = "failed"
                document.error_message = "No text could be extracted from the PDF"
                db.commit()
                return
        except Exception as e:
            logger.error(f"Text extraction failed for document {doc_id}: {e}")
            document.status = "failed"
            document.error_message = f"Text extraction failed: {str(e)}"
            db.commit()
            return
        
        # Update database with extracted text
        document.content = text_content
        db.commit()
        logger.info(f"Updated document {doc_id} with extracted text ({len(text_content)} chars)")
        
        # Index document in RAG system
        if rag_service:
            max_index_retries = 3
            for attempt in range(max_index_retries):
                try:
                    rag_service.index_document(doc_id, text_content)
                    logger.info(f"Indexed document {doc_id} in RAG system")
                    document.status = "indexed"
                    document.error_message = None  # Clear any previous error
                    db.commit()
                    break
                except Exception as e:
                    logger.warning(f"RAG indexing attempt {attempt+1} failed for document {doc_id}: {e}")
                    if attempt < max_index_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        logger.error(f"RAG indexing failed after {max_index_retries} attempts for document {doc_id}: {e}")
                        document.status = "processed"
                        document.error_message = f"RAG indexing failed after retries: {str(e)}"
                        db.commit()
        else:
            logger.warning("RAG service not available, document not indexed")
            document.status = "processed"
            db.commit()
        
        logger.info(f"Document {doc_id} processing completed successfully")
    
    except Exception as e:
        logger.error(f"Background processing failed for document {doc_id}: {e}", exc_info=True)
        try:
            document = db.query(Document).filter(Document.id == doc_id).first()
            if document:
                document.status = "failed"
                document.error_message = str(e)
                db.commit()
        except:
            pass
    finally:
        db.close()
        elapsed = time.time() - start_time
        logger.info(f"Completed processing document {doc_id} in {elapsed:.2f} seconds")

@app.get("/")
async def root():
    return FileResponse("frontend/build/index.html")

@app.get("/{path:path}")
async def serve_spa(path: str):
    # Serve index.html for all non-API routes (SPA routing)
    if path.startswith("api/") or path.startswith("static/"):
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse("frontend/build/index.html")

@app.post("/api/upload", response_model=DocumentResponse)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a PDF document"""
    logger.info(f"Upload request received: {file.filename} (content_type: {file.content_type})")
    
    try:
        # Validate file
        validate_file(file)
        
        # Generate unique filename to avoid conflicts
        import uuid
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Save the uploaded file
        try:
            file_path = save_uploaded_file(file, unique_filename)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
        # Store initial metadata in database
        document = Document(
            filename=file.filename,
            file_path=file_path,
            content="",
            status="uploaded"
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        logger.info(f"Document metadata stored: ID {document.id}, Status: {document.status}")
        
        # Start background processing
        background_tasks.add_task(process_and_index_document, document.id, file_path)
        
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            status=document.status,
            content_preview="Processing in progress...",
            error_message=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/documents", response_model=list[DocumentResponse])
async def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents"""
    documents = db.query(Document).all()
    return [
        DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            status=doc.status,
            content_preview=doc.content[:500] + "..." if doc.content and len(doc.content) > 500 else (doc.content or ""),
            error_message=doc.error_message
        )
        for doc in documents
    ]

@app.get("/api/documents/{document_id}/status", response_model=DocumentStatus)
async def get_document_status(document_id: int, db: Session = Depends(get_db)):
    """Get processing status of a specific document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Determine progress message based on status
    progress_messages = {
        "uploaded": "Document uploaded, waiting to be processed",
        "processing": "Extracting text and indexing document",
        "indexed": "Document fully processed and indexed",
        "processed": "Document processed (indexing unavailable)",
        "failed": "Processing failed"
    }
    
    return DocumentStatus(
        id=document.id,
        filename=document.filename,
        status=document.status,
        progress=progress_messages.get(document.status, "Unknown status"),
        error_message=document.error_message
    )

@app.post("/api/process", response_model=SummaryResponse)
async def process_document(
    request: ProcessingRequest,
    db: Session = Depends(get_db)
):
    """Process document with custom prompt using RAG"""
    logger.info(f"Processing request: query='{request.query[:100]}...', top_k={request.top_k}")
    
    try:
        # Retrieve relevant chunks using RAG
        relevant_chunks = []
        if rag_service:
            try:
                relevant_chunks = rag_service.search(request.query, k=request.top_k)
                logger.info(f"RAG search returned {len(relevant_chunks)} chunks")
            except Exception as e:
                logger.error(f"RAG search failed: {e}", exc_info=True)
                relevant_chunks = []
        else:
            logger.warning("RAG service not available")
            relevant_chunks = []
        
        # If no chunks found, provide helpful message
        if not relevant_chunks:
            # Check if any documents exist
            doc_count = db.query(Document).count()
            if doc_count == 0:
                return SummaryResponse(
                    query=request.query,
                    response="No documents have been uploaded yet. Please upload some PDF documents first.",
                    relevant_chunks=[]
                )
            else:
                # Documents exist but no matches found
                return SummaryResponse(
                    query=request.query,
                    response="No relevant content found in the uploaded documents for this query. Try rephrasing your question or uploading more relevant documents.",
                    relevant_chunks=[]
                )
        
        # Generate response using LLM
        if llm_service:
            try:
                response = llm_service.generate_response(
                    query=request.query,
                    context=relevant_chunks,
                    custom_prompt=request.custom_prompt
                )
                logger.info(f"LLM response generated ({len(response)} chars)")
            except Exception as e:
                logger.error(f"LLM generation failed: {e}", exc_info=True)
                response = f"Error generating LLM response: {str(e)}. Retrieved context chunks are available below."
        else:
            logger.warning("LLM service not available")
            response = "LLM service not available. Please configure GROK_API_KEY. Retrieved context chunks are shown below."
        
        return SummaryResponse(
            query=request.query,
            response=response,
            relevant_chunks=relevant_chunks
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/api/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get specific document details"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        status=document.status,
        content_preview=document.content or "",
        error_message=document.error_message
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app", 
        host="0.0.0.0", 
        port=8000,
        reload=False,
        # Configuration for file uploads
        limit_concurrency=10,
        limit_max_requests=None,
        timeout_keep_alive=300,  # 5 minutes keep-alive
        timeout_graceful_shutdown=30
    )