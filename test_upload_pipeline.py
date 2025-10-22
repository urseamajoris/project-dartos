#!/usr/bin/env python3
"""
Comprehensive test of the file upload pipeline
Tests: file upload, text extraction, API endpoints, and error handling
"""

import requests
import time
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000/api"
TEST_PDF = "sample_document.pdf"

def test_backend_health():
    """Test if backend is responding"""
    print("1. Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/documents")
        if response.status_code == 200:
            print("   ✅ Backend is healthy and responding")
            return True
        else:
            print(f"   ❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend is not responding: {e}")
        return False

def test_file_upload():
    """Test file upload functionality"""
    print("\n2. Testing file upload...")
    
    if not os.path.exists(TEST_PDF):
        print(f"   ❌ Test file {TEST_PDF} not found")
        return None
    
    try:
        with open(TEST_PDF, 'rb') as f:
            files = {'file': (TEST_PDF, f, 'application/pdf')}
            response = requests.post(f"{BACKEND_URL}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ File uploaded successfully")
            print(f"   - Document ID: {data['id']}")
            print(f"   - Filename: {data['filename']}")
            print(f"   - Status: {data['status']}")
            return data['id']
        else:
            print(f"   ❌ Upload failed with status {response.status_code}")
            print(f"   - Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        return None

def test_document_processing(doc_id):
    """Test document processing and status tracking"""
    print(f"\n3. Testing document processing (ID: {doc_id})...")
    
    max_wait = 30  # seconds
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BACKEND_URL}/documents/{doc_id}/status")
            if response.status_code == 200:
                data = response.json()
                status = data['status']
                progress = data.get('progress', '')
                error = data.get('error_message')
                
                print(f"   Status: {status} - {progress}")
                
                if status in ['indexed', 'processed']:
                    print(f"   ✅ Document processed successfully")
                    if error:
                        print(f"   ⚠️  Warning: {error}")
                    return True
                elif status == 'failed':
                    print(f"   ❌ Processing failed: {error}")
                    return False
                
                time.sleep(2)
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
            return False
    
    print(f"   ⚠️  Processing timeout after {max_wait} seconds")
    return False

def test_document_retrieval(doc_id):
    """Test retrieving document details"""
    print(f"\n4. Testing document retrieval (ID: {doc_id})...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/documents/{doc_id}")
        if response.status_code == 200:
            data = response.json()
            content = data.get('content_preview', '')
            print(f"   ✅ Document retrieved successfully")
            print(f"   - Content length: {len(content)} characters")
            if content:
                print(f"   - Preview: {content[:100]}...")
            return True
        else:
            print(f"   ❌ Retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Retrieval error: {e}")
        return False

def test_rag_query():
    """Test RAG query endpoint"""
    print("\n5. Testing RAG query endpoint...")
    
    try:
        payload = {
            "query": "What are the main features of this system?",
            "top_k": 3
        }
        response = requests.post(
            f"{BACKEND_URL}/process",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ RAG query successful")
            print(f"   - Query: {data['query']}")
            print(f"   - Chunks retrieved: {len(data['relevant_chunks'])}")
            print(f"   - Response preview: {data['response'][:150]}...")
            return True
        else:
            print(f"   ❌ Query failed: {response.status_code}")
            print(f"   - Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Query error: {e}")
        return False

def test_grok_api_integration():
    """Test GROK API integration"""
    print("\n6. Testing GROK API integration...")
    
    grok_key = os.getenv('GROK_API_KEY', 'not_set')
    
    if grok_key == 'not_set' or grok_key == 'your_grok_api_key_here':
        print("   ⚠️  GROK_API_KEY not configured - LLM features disabled")
        print("   - To enable: Set GROK_API_KEY in .env file")
        print("   - Get key from: https://console.x.ai/")
        return False
    else:
        print("   ✅ GROK_API_KEY is configured")
        print("   - Note: Actual API calls require valid key and network access")
        return True

def main():
    print("=" * 70)
    print("DARTOS FILE UPLOAD PIPELINE - COMPREHENSIVE TEST")
    print("=" * 70)
    
    results = []
    
    # Test 1: Backend health
    results.append(("Backend Health", test_backend_health()))
    
    if not results[0][1]:
        print("\n❌ Backend is not running. Please start it first:")
        print("   cd backend && uvicorn main:app --reload")
        return
    
    # Test 2: File upload
    doc_id = test_file_upload()
    results.append(("File Upload", doc_id is not None))
    
    if doc_id:
        # Test 3: Document processing
        results.append(("Document Processing", test_document_processing(doc_id)))
        
        # Test 4: Document retrieval
        results.append(("Document Retrieval", test_document_retrieval(doc_id)))
    
    # Test 5: RAG query
    results.append(("RAG Query", test_rag_query()))
    
    # Test 6: GROK API
    results.append(("GROK API Integration", test_grok_api_integration()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print("\n" + "-" * 70)
    print(f"Results: {passed_count}/{total_count} tests passed")
    print("=" * 70)
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! File upload pipeline is fully functional.")
    elif passed_count >= total_count - 1:
        print("\n✅ Core functionality working! Minor issues detected.")
    else:
        print("\n⚠️  Some critical tests failed. Please review the errors above.")

if __name__ == "__main__":
    main()
