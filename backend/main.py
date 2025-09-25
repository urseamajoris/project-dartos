from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from database import SessionLocal, engine
from models import Base, Document
from services.pdf_processor import PDFProcessor
try:
    from services.llm_service import LLMService
    from services.rag_service import RAGService
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some services could not be imported: {e}")
    SERVICES_AVAILABLE = False
from schemas import DocumentResponse, ProcessingRequest, SummaryResponse

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure FastAPI with larger file upload limits
app = FastAPI(
    title="Dartos - Agentic Info Services", 
    version="1.0.0"
)# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files from React build
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# Initialize services
pdf_processor = PDFProcessor()
if SERVICES_AVAILABLE:
    llm_service = LLMService()
    rag_service = RAGService()
else:
    llm_service = None
    rag_service = None

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a PDF document"""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process PDF
        text_content = pdf_processor.extract_text(file_path)
        
        # Store metadata in database
        document = Document(
            filename=file.filename,
            file_path=file_path,
            content=text_content
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Index document in RAG system
        if rag_service:
            rag_service.index_document(document.id, text_content)
        else:
            print("Warning: RAG service not available, document not indexed")
        
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            status="processed",
            content_preview=text_content[:500] + "..." if len(text_content) > 500 else text_content
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/api/documents", response_model=list[DocumentResponse])
async def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents"""
    documents = db.query(Document).all()
    return [
        DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            status="processed",
            content_preview=doc.content[:500] + "..." if len(doc.content) > 500 else doc.content
        )
        for doc in documents
    ]

@app.post("/api/process", response_model=SummaryResponse)
async def process_document(
    request: ProcessingRequest,
    db: Session = Depends(get_db)
):
    """Process document with custom prompt using RAG"""
    try:
        # Retrieve relevant chunks using RAG
        if rag_service:
            relevant_chunks = rag_service.search(request.query, k=request.top_k)
        else:
            relevant_chunks = ["RAG service not available"]
        
        # Generate response using LLM
        if llm_service:
            response = llm_service.generate_response(
                query=request.query,
                context=relevant_chunks,
                custom_prompt=request.custom_prompt
            )
        else:
            response = "LLM service not available. Please configure GROK_API_KEY."
        
        return SummaryResponse(
            query=request.query,
            response=response,
            relevant_chunks=relevant_chunks
        )
        
    except Exception as e:
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
        status="processed",
        content_preview=document.content
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app", 
        host="0.0.0.0", 
        port=8000,
        reload=False,
        # Basic configuration for file uploads
        limit_concurrency=10,
        limit_max_requests=None
    )