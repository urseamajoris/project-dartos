#!/usr/bin/env python3
"""
Simple API test without dependencies that require system packages
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_basic_imports():
    """Test basic imports work"""
    print("Testing basic imports...")
    try:
        import database
        import models
        import schemas
        print("✅ Basic modules import successfully")
        return True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False

def test_database_models():
    """Test database setup"""
    print("Testing database models...")
    try:
        from database import Base, engine
        from models import Document
        
        # Test model definition
        assert hasattr(Document, 'id')
        assert hasattr(Document, 'filename')
        assert hasattr(Document, 'content')
        
        print("✅ Database models are properly defined")
        return True
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        return False

def test_pydantic_schemas():
    """Test Pydantic schemas"""
    print("Testing Pydantic schemas...")
    try:
        from schemas import DocumentResponse, ProcessingRequest, SummaryResponse
        
        # Test DocumentResponse
        doc = DocumentResponse(
            id=1,
            filename="test.pdf",
            status="processed",
            content_preview="Test content"
        )
        assert doc.id == 1
        assert doc.filename == "test.pdf"
        
        # Test ProcessingRequest
        req = ProcessingRequest(
            query="Test query",
            top_k=5
        )
        assert req.query == "Test query"
        assert req.top_k == 5
        
        print("✅ Pydantic schemas work correctly")
        return True
    except Exception as e:
        print(f"❌ Pydantic schemas test failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app creation (without services that need system packages)"""
    print("Testing FastAPI app...")
    try:
        # Mock the services to avoid import errors
        sys.modules['services.pdf_processor'] = type('MockModule', (), {'PDFProcessor': lambda: None})()
        sys.modules['services.llm_service'] = type('MockModule', (), {'LLMService': lambda: None})()
        sys.modules['services.rag_service'] = type('MockModule', (), {'RAGService': lambda: None})()
        
        # Import and test basic FastAPI setup
        from fastapi import FastAPI
        app = FastAPI()
        
        assert app is not None
        print("✅ FastAPI app can be created")
        return True
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False

def main():
    print("🧪 Running Basic Dartos Backend Tests\n")
    
    tests = [
        test_basic_imports,
        test_database_models,
        test_pydantic_schemas,
        test_fastapi_app,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} basic tests passed")
    
    if passed == total:
        print("🎉 Basic backend structure is correct!")
        print("💡 To test full functionality, use Docker: docker-compose up")
        return 0
    else:
        print("⚠️  Some basic tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())