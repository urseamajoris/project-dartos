# Dartos - Agentic Automated Info Services

A comprehensive framework for intelligent document processing and analysis using React frontend, FastAPI backend, and AI-powered document understanding.

## 🚀 Features

- **PDF Upload & Processing**: Upload PDF documents with automatic text extraction and OCR fallback
- **Intelligent Metadata Storage**: SQL database for efficient document metadata and content storage
- **LLM Integration**: Advanced language model integration using xAI's Grok for document analysis
- **RAG System**: Retrieval-Augmented Generation for contextual document querying
- **Interactive Dashboard**: Custom prompts and intelligent summaries/explanations
- **Localhost Preview**: Complete Docker setup for easy local development

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │◄──►│  FastAPI Backend │◄──►│  SQL Database   │
│   (Port 3000)   │    │   (Port 8000)    │    │  (PostgreSQL)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   AI Services    │
                       │  • OpenAI LLM    │
                       │  • ChromaDB RAG  │
                       │  • OCR Engine    │
                       └──────────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **React 18** with Material-UI components
- **React Router** for navigation
- **Axios** for API communication
- **React Dropzone** for file uploads

### Backend
- **FastAPI** for high-performance API
- **SQLAlchemy** for database ORM
- **ChromaDB** for vector storage and RAG
- **xAI Grok API** for LLM integration
- **Tesseract OCR** for text extraction
- **pdf2image** for PDF processing

### Infrastructure
- **Docker & Docker Compose** for containerization
- **PostgreSQL** for production database
- **SQLite** for development

## 🚦 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key (optional, for LLM features)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd project-dartos
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` file:
```bash
# Add your OpenAI API key for LLM features
OPENAI_API_KEY=your_openai_api_key_here

# Database configuration (optional)
DATABASE_URL=sqlite:///./dartos.db
```

### 3. Start Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📋 Usage Workflow

### 1. Upload Documents
- Navigate to the Home page
- Drag & drop PDF files or click to select
- System automatically extracts text using OCR if needed
- Documents are processed and stored with metadata

### 2. View Documents
- Go to Documents page to see all uploaded files
- View document content and processing status
- Click "View" to see full document content

### 3. Analyze with AI
- Use the Dashboard to query your documents
- Enter natural language questions
- Customize prompts for specific analysis types
- Adjust retrieval parameters (top-K chunks)

### 4. Example Queries
- "Summarize the main points of the document"
- "What are the key findings?"
- "Extract important dates and events"
- "List recommendations or action items"

## 🔧 Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Database Migration
```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 📁 Project Structure

```
project-dartos/
├── backend/
│   ├── services/
│   │   ├── pdf_processor.py    # PDF text extraction & OCR
│   │   ├── llm_service.py      # OpenAI integration
│   │   └── rag_service.py      # ChromaDB vector storage
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Database models
│   ├── schemas.py              # Pydantic schemas
│   └── database.py             # Database configuration
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   └── services/           # API services
│   └── public/
├── docker-compose.yml          # Container orchestration
└── README.md                   # This file
```

## 🔌 API Endpoints

### Document Management
- `POST /upload` - Upload PDF documents
- `GET /documents` - List all documents
- `GET /documents/{id}` - Get specific document

### AI Processing
- `POST /process` - Process documents with custom queries
- Query parameters: `query`, `custom_prompt`, `top_k`

### Health Check
- `GET /` - API status and information

## 🎯 Configuration Options

### Environment Variables
```bash
# Required for LLM features
XAI_API_KEY=your_xai_api_key

# Database
DATABASE_URL=sqlite:///./dartos.db

# Optional: Use PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost:5432/dartos
```

### Docker Compose Customization
- Modify `docker-compose.yml` for different ports
- Add environment variables for production
- Configure volume mounts for persistent storage

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🐛 Troubleshooting

### Common Issues

1. **OCR not working**: Ensure Tesseract is installed
2. **Upload fails**: Check file permissions in uploads directory
3. **LLM errors**: Verify xAI API key is set correctly
4. **Database issues**: Check database URL and permissions

### Logs
```bash
# View all service logs
docker-compose logs

# View specific service
docker-compose logs backend
docker-compose logs frontend
```

## 🔮 Future Enhancements

- [ ] Support for additional file formats (Word, Excel, etc.)
- [ ] Advanced OCR with layout detection
- [ ] Multi-language support
- [ ] User authentication and authorization
- [ ] Document versioning and history
- [ ] Batch processing capabilities
- [ ] Export results to various formats
- [ ] Integration with cloud storage providers

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or issues, please open a GitHub issue or contact the development team.
