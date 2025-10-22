from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    filename: str
    status: str
    content_preview: str
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class DocumentStatus(BaseModel):
    id: int
    filename: str
    status: str
    progress: str
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProcessingRequest(BaseModel):
    query: str
    custom_prompt: Optional[str] = None
    top_k: int = 5

class SummaryResponse(BaseModel):
    query: str
    response: str
    relevant_chunks: List[str]

class LogEntry(BaseModel):
    level: str
    message: str
    data: Optional[Any] = None
    timestamp: str