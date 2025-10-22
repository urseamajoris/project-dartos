# Quick Reference Guide - File Upload & Processing Improvements

## For Users

### Uploading Files

1. **File Size Limit**: You can now upload PDFs up to **50MB** (previously 10MB)

2. **Upload Progress**: 
   - Watch the progress bar as your file uploads
   - See percentage completion in real-time

3. **Processing Status**:
   After upload, you'll see one of these statuses:
   - 🔄 **Processing** - Extracting text and indexing
   - ✅ **Indexed** - Ready to use in queries
   - ⚠️ **Failed** - Something went wrong (see error message)

4. **Error Messages**:
   - If processing fails, you'll see a clear error message
   - Common issues: corrupted PDF, no extractable text, network timeout

### Using the Dashboard

1. **Query Documents**:
   - Upload PDFs first
   - Wait for "Indexed" status
   - Enter your question in the dashboard
   - Get AI-generated answers with context

2. **Context Sections**:
   - Answers now reference specific sections (e.g., "According to Context Section 2...")
   - This helps you trace information back to source

## For Developers

### Running the Application

```bash
# Option 1: Docker (Recommended)
docker compose up

# Option 2: Local Development
python run.py

# Option 3: Manual Setup
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migration

If you have an existing database, run the migration:

```bash
python migrate_database.py
```

This adds `status` and `error_message` columns to the documents table.

### API Changes

#### New Endpoint
```
GET /api/documents/{id}/status

Response:
{
  "id": 1,
  "filename": "document.pdf",
  "status": "processing",
  "progress": "Extracting text and indexing document",
  "error_message": null
}
```

#### Modified Endpoints

**POST /api/upload**
```json
Response includes:
{
  "status": "uploaded",
  "error_message": null
}
```

**GET /api/documents**
```json
Each document includes:
{
  "status": "indexed",
  "error_message": null
}
```

### Frontend Integration

**Poll for Status Updates**:
```javascript
import { documentService } from './services/api';

// After upload
const result = await documentService.uploadDocument(file);

// Poll for status
const pollStatus = async (docId) => {
  const status = await documentService.getDocumentStatus(docId);
  
  if (status.status === 'processing' || status.status === 'uploaded') {
    setTimeout(() => pollStatus(docId), 2000); // Poll every 2 seconds
  }
};

pollStatus(result.id);
```

**Upload with Progress**:
```javascript
await documentService.uploadDocument(file, (progressEvent) => {
  const percentCompleted = Math.round(
    (progressEvent.loaded * 100) / progressEvent.total
  );
  console.log(`Upload progress: ${percentCompleted}%`);
});
```

### Configuration

#### Backend (main.py)
```python
# File size limit
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Timeout settings (uvicorn)
timeout_keep_alive=300  # 5 minutes
```

#### Frontend (api.js)
```javascript
// Request timeout
timeout: 300000  // 5 minutes
```

### Status Values

| Status | Meaning | Next Action |
|--------|---------|-------------|
| uploaded | File saved, waiting for processing | Background task will start |
| processing | Text extraction in progress | Wait for completion |
| indexed | Successfully indexed in RAG | Ready for queries |
| processed | Text extracted, RAG unavailable | Can view content |
| failed | Processing error occurred | Check error_message |

### Error Handling

**Backend (background task)**:
```python
try:
    # Process document
    text_content = pdf_processor.extract_text(file_path)
    document.status = "processing"
    db.commit()
    
    # Index in RAG
    rag_service.index_document(doc_id, text_content)
    document.status = "indexed"
    db.commit()
    
except Exception as e:
    document.status = "failed"
    document.error_message = str(e)
    db.commit()
```

**Frontend (upload handling)**:
```javascript
try {
  const result = await documentService.uploadDocument(file);
  // Success - start polling
} catch (err) {
  if (err.code === 'ECONNABORTED') {
    showError('Upload timeout - file too large or network slow');
  } else {
    showError(err);
  }
}
```

### Testing

**Run all tests**:
```bash
# Basic tests
python test_basic.py

# Workflow tests
python test_upload_workflow.py

# Security scan
# (automated in CI/CD)
```

**Create a test PDF**:
```bash
python create_sample_pdf.py
```

### Troubleshooting

**Upload times out**:
- File may be larger than 50MB
- Network connection is slow
- Backend server is not responding
- Check browser console for specific error

**Processing stuck in "processing"**:
- Check backend logs for errors
- Verify background task is running
- Database may be locked (SQLite)

**RAG indexing fails**:
- ChromaDB may not be initialized
- Embedding model download failed (offline)
- Check logs for specific error

**No results from queries**:
- Verify documents are in "indexed" status
- Check if any documents uploaded
- RAG service may be unavailable

### Monitoring

**Check processing status**:
```bash
# View all documents with status
curl http://localhost:8000/api/documents

# Check specific document
curl http://localhost:8000/api/documents/1/status
```

**Backend logs**:
```bash
# Look for these log messages
INFO:main:Upload request received
INFO:main:Document metadata stored: ID 1, Status: uploaded
INFO:main:Starting background processing for document 1
INFO:services.pdf_processor:Direct text extraction yielded 5000 characters
INFO:services.rag_service:Indexed document 1 with 5 chunks
INFO:main:Updated document 1 with extracted text
```

### Best Practices

1. **Always wait for "indexed" status** before querying
2. **Check error_message** if status is "failed"
3. **Use progress callbacks** for better UX
4. **Implement retry logic** for network failures
5. **Log upload metrics** for monitoring
6. **Test with various PDF types** (text, scanned, images)

### Performance Tips

1. **Optimize PDF size** before upload (compress if needed)
2. **Use text PDFs** instead of scanned for faster processing
3. **Upload during off-peak hours** for large batches
4. **Monitor ChromaDB size** for storage planning
5. **Implement cleanup** for old/unused documents

## Common Workflows

### Basic Upload & Query
```
1. Upload PDF → Wait for "indexed"
2. Go to Dashboard → Enter query
3. Get AI answer with context citations
```

### Batch Upload
```
1. Select multiple PDFs (up to 50MB each)
2. Upload all at once
3. Monitor status for each document
4. Query when all are "indexed"
```

### Error Recovery
```
1. Check error_message for failed documents
2. Fix the issue (re-scan PDF, reduce size, etc.)
3. Re-upload the document
4. Processing starts automatically
```

## Support

For issues or questions:
1. Check IMPROVEMENTS_SUMMARY.md for detailed information
2. Review backend logs for error details
3. Check GitHub issues for similar problems
4. Open a new issue with error logs and steps to reproduce
