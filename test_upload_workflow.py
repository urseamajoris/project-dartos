#!/usr/bin/env python3
"""
Test file upload workflow and status tracking
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_schemas():
    """Test new schema additions"""
    print("Testing schemas...")
    try:
        from schemas import DocumentResponse, DocumentStatus, ProcessingRequest, SummaryResponse
        
        # Test DocumentResponse with new fields
        doc = DocumentResponse(
            id=1,
            filename="test.pdf",
            status="processing",
            content_preview="Test content",
            error_message="Test error"
        )
        assert doc.error_message == "Test error"
        
        # Test DocumentStatus
        status = DocumentStatus(
            id=1,
            filename="test.pdf",
            status="processing",
            progress="Extracting text and indexing document",
            error_message=None
        )
        assert status.progress == "Extracting text and indexing document"
        
        print("✅ Schemas work correctly with new fields")
        return True
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

def test_document_model():
    """Test document model with new fields"""
    print("Testing document model...")
    try:
        from database import Base, engine
        from models import Document
        
        # Check model has new fields
        assert hasattr(Document, 'status')
        assert hasattr(Document, 'error_message')
        
        print("✅ Document model has status and error_message fields")
        return True
    except Exception as e:
        print(f"❌ Document model test failed: {e}")
        return False

def test_llm_service():
    """Test LLM service improvements"""
    print("Testing LLM service...")
    try:
        from services.llm_service import LLMService
        
        # Initialize without API key (graceful degradation)
        os.environ.pop('GROK_API_KEY', None)
        llm = LLMService()
        
        # Test chunk formatting
        chunks = [
            "This is the first chunk of text.",
            "This is the second chunk with more information.",
            "Third chunk contains additional details."
        ]
        
        formatted = llm._format_chunks_for_context(chunks)
        
        # Check formatting includes section numbers
        assert "[Context Section 1]" in formatted
        assert "[Context Section 2]" in formatted
        assert "[Context Section 3]" in formatted
        assert "---" in formatted  # Check separator
        
        print("✅ LLM service chunk formatting works correctly")
        return True
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_service_offline():
    """Test RAG service handles offline mode gracefully"""
    print("Testing RAG service offline mode...")
    try:
        import tempfile
        from services.rag_service import RAGService
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            rag = RAGService(chroma_path=temp_dir)
            
            # Should initialize even without embedding model
            assert rag.client is not None
            assert rag.collection is not None
            
            # Test chunking
            test_text = "This is a test document. " * 50
            chunks = rag.chunk_text(test_text)
            assert len(chunks) > 0
            
            print("✅ RAG service works in offline mode")
            return True
    except Exception as e:
        print(f"❌ RAG service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_processing():
    """Test end-to-end document processing pipeline"""
    print("Testing end-to-end document processing...")
    try:
        from services.pdf_processor import PDFProcessor
        from services.rag_service import RAGService
        from services.llm_service import LLMService
        import tempfile
        import os
        
        # Create sample PDF if it doesn't exist
        sample_pdf = "sample_document.pdf"
        if not os.path.exists(sample_pdf):
            try:
                from create_sample_pdf import create_sample_pdf
                create_sample_pdf()
            except (ImportError, Exception) as e:
                print(f"⚠️ Cannot create sample PDF: {e}")
                print("⚠️ Skipping end-to-end test - no test PDF available")
                return False
        
        if not os.path.exists(sample_pdf):
            print("⚠️ Sample PDF not available, skipping end-to-end test")
            return False
        
        # Initialize services
        pdf_processor = PDFProcessor()
        with tempfile.TemporaryDirectory() as temp_dir:
            rag_service = RAGService(chroma_path=temp_dir)
            llm_service = LLMService()
            
            # Extract text
            text = pdf_processor.extract_text(sample_pdf)
            assert text and len(text) > 100, "Text extraction failed"
            
            # Chunk and index
            doc_id = 999  # Test ID
            rag_service.index_document(doc_id, text)
            
            # Test search
            results = rag_service.search("What are the main features?", k=3)
            assert len(results) > 0, "RAG search failed"
            
            # Test LLM response (if API key available)
            if llm_service.client:
                response = llm_service.generate_response(
                    "What are the main features of this system?",
                    results
                )
                assert response and len(response) > 10, "LLM response failed"
            
            print("✅ End-to-end processing test passed")
            return True
    
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 Running File Upload Workflow Tests\n")
    
    tests = [
        test_schemas,
        test_document_model,
        test_llm_service,
        test_rag_service_offline,
        test_end_to_end_processing,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All workflow tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
