#!/usr/bin/env python3
"""
Create a sample PDF for testing the Dartos system
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_sample_pdf():
    """Create a sample PDF with test content"""
    filename = "sample_document.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Sample Document for Dartos Testing")
    
    # Add content
    c.setFont("Helvetica", 12)
    y_position = 700
    
    content = [
        "This is a sample document created for testing the Dartos framework.",
        "",
        "Key Features Tested:",
        "• PDF upload and text extraction",
        "• Metadata storage in SQL database",
        "• LLM integration for intelligent analysis",
        "• RAG system for contextual retrieval",
        "• Custom prompt processing",
        "",
        "Sample Analysis Questions:",
        "1. What are the main features of this system?",
        "2. How does the document processing work?",
        "3. What technologies are used in this framework?",
        "",
        "Technical Implementation:",
        "The Dartos framework uses a React frontend with Material-UI components",
        "for user interaction, FastAPI backend for high-performance API services,",
        "and integrates with OpenAI's language models for intelligent document",
        "analysis. The system supports OCR fallback for scanned documents and",
        "uses ChromaDB for vector storage in the RAG pipeline.",
        "",
        "Future Enhancements:",
        "• Support for additional file formats",
        "• Multi-language document processing",
        "• Advanced analytics and reporting",
        "• Integration with cloud storage providers",
        "• Real-time collaboration features"
    ]
    
    for line in content:
        c.drawString(100, y_position, line)
        y_position -= 20
        if y_position < 100:  # Start new page if needed
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = 750
    
    c.save()
    print(f"✅ Created sample PDF: {filename}")
    return filename

if __name__ == "__main__":
    try:
        create_sample_pdf()
    except ImportError:
        print("⚠️ reportlab not installed. Install with: pip install reportlab")
        print("   For testing, you can use any PDF file instead.")