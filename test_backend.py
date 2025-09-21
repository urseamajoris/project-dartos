#!/usr/bin/env python3
"""
Simple test script to verify the backend services work correctly
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_pdf_processor():
    """Test PDF processing service"""
    print("Testing PDF Processor...")
    try:
        from services.pdf_processor import PDFProcessor
        processor = PDFProcessor()
        print("✅ PDF Processor initialized successfully")
        return True
    except Exception as e:
        print(f"❌ PDF Processor failed: {e}")
        return False

def test_llm_service():
    """Test LLM service (without API key)"""
    print("Testing LLM Service...")
    try:
        from services.llm_service import LLMService
        # Don't initialize with real API key for testing
        print("✅ LLM Service can be imported")
        return True
    except Exception as e:
        print(f"❌ LLM Service failed: {e}")
        return False

def test_rag_service():
    """Test RAG service"""
    print("Testing RAG Service...")
    try:
        from services.rag_service import RAGService
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['CHROMA_DB_PATH'] = temp_dir
            rag = RAGService()
            
            # Test basic functionality
            test_text = "This is a test document for RAG functionality."
            rag.index_document(1, test_text)
            results = rag.search("test document", k=1)
            
            if results and len(results) > 0:
                print("✅ RAG Service working correctly")
                return True
            else:
                print("❌ RAG Service search returned no results")
                return False
    except Exception as e:
        print(f"❌ RAG Service failed: {e}")
        return False

def test_database():
    """Test database models"""
    print("Testing Database Models...")
    try:
        from database import Base, engine
        from models import Document
        Base.metadata.create_all(bind=engine)
        print("✅ Database models work correctly")
        return True
    except Exception as e:
        print(f"❌ Database models failed: {e}")
        return False

def main():
    print("🧪 Running Dartos Backend Tests\n")
    
    tests = [
        test_database,
        test_pdf_processor,
        test_llm_service,
        test_rag_service,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is ready to go.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())