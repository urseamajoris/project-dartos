"""
Dartos - Agentic Automated Info Services Backend
FastAPI application for PDF processing, AI analysis, and RAG-based document querying.
"""

import logging
import os
import re
import time
import uuid
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Document
from schemas import DocumentResponse, DocumentStatus, LogEntry, ProcessingRequest, SummaryResponse
from services.pdf_processor import PDFProcessor

# Try to import optional services
try:
    from services.llm_service import LLMService
    from services.rag_service import RAGService
    SERVICES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some services could not be imported: {e}")
    SERVICES_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'.pdf'}
UPLOAD_DIR = Path("uploads")
FRONTEND_BUILD_DIR = Path("frontend/build")

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize services
pdf_processor = PDFProcessor()
llm_service = LLMService() if SERVICES_AVAILABLE else None
rag_service = RAGService() if SERVICES_AVAILABLE else None

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
if FRONTEND_BUILD_DIR.exists():
    static_dir = FRONTEND_BUILD_DIR / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    else:
        logger.warning("Frontend build static directory not found, skipping static file mount")
else:
    logger.warning("Frontend build directory not found, skipping static file mount")

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

def _extract_and_validate_text(pdf_processor: PDFProcessor, file_path: str) -> tuple[str, bool, str]:
    """Extract text from PDF and validate its quality"""
    try:
        text_content = pdf_processor.extract_text(file_path)

        # Validate extracted text
        validation_result = _validate_extracted_text(text_content)
        if not validation_result['is_valid']:
            return "", False, f"Text extraction validation failed: {validation_result['reason']}"

        if not text_content.strip():
            return "", False, "No text could be extracted from the PDF"

        return text_content, True, ""
    except Exception as e:
        return "", False, f"Text extraction failed: {str(e)}"


def _index_document_with_rag(rag_service, doc_id: int, text_content: str) -> tuple[str, str]:
    """Index document in RAG system with retry logic"""
    if not rag_service:
        return "processed", "RAG service not available, document not indexed"

    max_index_retries = 3
    for attempt in range(max_index_retries):
        try:
            rag_service.index_document(doc_id, text_content)
            return "indexed", None
        except Exception as e:
            if attempt < max_index_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return "processed", f"RAG indexing failed after retries: {str(e)}"

    return "processed", "RAG indexing failed after retries"


def process_and_index_document(doc_id: int, file_path: str):
    """Background task to process and index document"""
    start_time = time.time()
    logger.info(f"Starting background processing for document {doc_id}")

    db = SessionLocal()
    try:
        # Update status to processing
        document = db.query(Document).filter(Document.id == doc_id).first()
        if not document:
            logger.error(f"Document {doc_id} not found")
            return

        document.status = "processing"
        db.commit()

        # Extract and validate text
        text_content, success, error_msg = _extract_and_validate_text(pdf_processor, file_path)
        if not success:
            document.status = "failed"
            document.error_message = error_msg
            db.commit()
            return

        # Update database with extracted text
        document.content = text_content
        db.commit()
        logger.info(f"Updated document {doc_id} with extracted text ({len(text_content)} chars)")

        # Index document in RAG system
        final_status, rag_error = _index_document_with_rag(rag_service, doc_id, text_content)
        document.status = final_status
        document.error_message = rag_error
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
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # Save the uploaded file
        file_path = save_uploaded_file(file, unique_filename)

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

@app.post("/api/log")
async def log_frontend(log_entry: LogEntry):
    """Receive logs from frontend"""
    level = log_entry.level.upper()
    message = f"[FRONTEND] {log_entry.message}"
    if log_entry.data:
        message += f" | Data: {log_entry.data}"
    
    if level == "DEBUG":
        logger.debug(message)
    elif level == "INFO":
        logger.info(message)
    elif level == "WARN":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    else:
        logger.info(f"[{level}] {message}")
    
    return {"status": "logged"}

# Catch-all routes for SPA - MUST be defined last
@app.get("/")
async def root():
    return FileResponse("frontend/build/index.html")

@app.get("/{path:path}")
async def serve_spa(path: str):
    # Serve index.html for all non-API routes (SPA routing)
    if path.startswith("api/") or path.startswith("static/"):
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse("frontend/build/index.html")

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