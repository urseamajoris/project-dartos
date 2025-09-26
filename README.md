# Dartos - Agentic Automated Info Services

A comprehensive framework for intelligent document processing and analysis using React frontend, FastAPI backend, and AI-powered document understanding.

## 🚀 Features

- **🚀 Enhanced Bootstrap Script**: Intelligent dependency management with network resilience and multiple fallback strategies
- **📄 PDF Upload & Processing**: Upload PDF documents with automatic text extraction and OCR fallback
- **🗄️ Intelligent Database Storage**: PostgreSQL for efficient document metadata and content storage
- **🤖 LLM Integration**: Advanced language model integration using xAI's Grok and OpenAI for document analysis
- **🔍 RAG System**: Retrieval-Augmented Generation with ChromaDB for contextual document querying
- **📊 Interactive Dashboard**: Custom prompts and intelligent summaries/explanations
- **🐳 Docker Integration**: Complete containerized setup with automatic service orchestration
- **🔧 Development Ready**: Hot-reload, comprehensive error handling, and troubleshooting guidance

## 🏗️ Enhanced Architecture

### System Overview
```
                    🚀 Bootstrap Script (run.py)
                         │
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │                 🐳 Docker Layer                          │
    │  ┌─────────────────┐              ┌─────────────────┐    │
    │  │   PostgreSQL    │              │  Optional: React │    │
    │  │   Database      │              │   Frontend      │    │
    │  │  (Port 5432)    │              │  (Port 3000)    │    │
    │  └─────────────────┘              └─────────────────┘    │
    └─────────────────────────────────────────────────────────┘
                         │                        │
                         ▼                        ▼
    ┌─────────────────────────────────────────────────────────┐
    │               📡 FastAPI Backend                        │
    │                  (Port 8000)                           │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
    │  │ PDF Processor│  │ AI Services │  │ RAG System  │     │
    │  │ • OCR       │  │ • OpenAI    │  │ • ChromaDB  │     │
    │  │ • Text Ext. │  │ • xAI Grok  │  │ • Embedding │     │
    │  └─────────────┘  └─────────────┘  └─────────────┘     │
    └─────────────────────────────────────────────────────────┘
```

### Bootstrap Process Flow
```
🚀 python run.py
    │
    ├── 🔍 Check Docker Installation & Daemon
    │
    ├── 📦 Smart Dependency Management
    │   ├── Install system packages (apt/yum)
    │   ├── Try bulk pip install from requirements.txt
    │   ├── Fallback: Individual package installation
    │   ├── Fallback: No-deps installation
    │   └── Final check: Import validation
    │
    ├── 🐳 PostgreSQL Docker Setup
    │   ├── Check existing containers
    │   ├── Pull postgres:13 image
    │   ├── Start container with health checks
    │   └── Validate database connectivity
    │
    ├── ⚙️ Environment Configuration
    │   ├── Set DATABASE_URL
    │   ├── Create uploads/ directory
    │   └── Create backend/chroma_db/ directory
    │
    └── 🌐 FastAPI Server Launch
        ├── Test Python imports
        ├── Check port availability
        └── Start uvicorn server
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
- **Docker and Docker Compose** (Required)
- **Python 3.11+** (for local development)
- **Internet connection** (for package installation)
- **Git** (to clone the repository)

### Option 1: Docker Compose (Recommended)
For the most reliable setup with all dependencies pre-installed:

```bash
# Clone the repository
git clone <repository-url>
cd project-dartos

# Start all services with Docker Compose
docker compose up

# Or run in background
docker compose up -d
```

**Docker Compose includes:**
- FastAPI backend with all Python dependencies
- PostgreSQL database
- React frontend (if configured)
- Volume persistence for data
- Automatic service networking

### Option 2: Enhanced Bootstrap Script
Use the intelligent bootstrap script that handles dependency installation automatically:

```bash
# Clone the repository
git clone <repository-url>
cd project-dartos

# Check if Docker Compose is available
python run.py --docker-check

# Run the enhanced bootstrap script
python run.py
```

**The bootstrap script intelligently:**
1. **Installs system dependencies** (build tools, PostgreSQL client)
2. **Manages Python packages** with multiple fallback strategies
3. **Starts PostgreSQL** in Docker with health checks
4. **Sets up environment** variables and directories
5. **Launches FastAPI server** on port 8000 with comprehensive error handling

**Bootstrap Script Options:**
```bash
python run.py --help           # Show comprehensive help
python run.py --skip-install   # Skip Python package installation
python run.py --docker-check   # Check Docker Compose availability
```

**Network Resilience Features:**
- Detects PyPI connectivity issues
- Multiple installation strategies (bulk → individual → no-deps)
- Recommends Docker Compose when packages fail
- Provides specific troubleshooting guidance

### Option 3: Manual Development Setup
For advanced users who want full control:

```bash
# 1. Clone and setup
git clone <repository-url>
cd project-dartos

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Start PostgreSQL (using Docker)
docker run -d \
  --name dartos-postgres \
  -e POSTGRES_DB=dartos \
  -e POSTGRES_USER=dartos \
  -e POSTGRES_PASSWORD=dartos123 \
  -p 5432:5432 \
  postgres:13

# 5. Set environment variables
export DATABASE_URL="postgresql://dartos:dartos123@localhost:5432/dartos"

# 6. Start the server
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Access Your Application

Once started (any method), access your application at:
- **🌐 Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **🗄️ Database**: PostgreSQL on localhost:5432 (if using bootstrap/manual)

## 🔧 Troubleshooting

### Common Issues & Solutions

**🐛 Package Installation Fails**
```bash
# Network issues with PyPI
python run.py --docker-check  # Check Docker alternative
docker compose up             # Use containerized setup

# Or try manual installation
python -m venv venv && source venv/bin/activate
pip install --timeout 120 -r backend/requirements.txt
python run.py --skip-install
```

**🐳 Docker Issues**
```bash
# Check Docker is running
docker info

# Clean up old containers
docker stop dartos-postgres && docker rm dartos-postgres

# Check Docker Compose
docker compose config
```

**🗄️ Database Connection Issues**
```bash
# Check PostgreSQL container
docker ps | grep postgres
docker logs dartos-postgres

# Test connection
docker exec dartos-postgres pg_isready -U dartos
```

**🚀 Server Startup Problems**
```bash
# Check Python path and imports
python -c "import fastapi, uvicorn, sqlalchemy; print('All imports OK')"

# Check port availability
netstat -tulpn | grep 8000

# View detailed logs
python run.py  # Check bootstrap output for specific errors
```

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
├── 🚀 run.py                     # Enhanced bootstrap script
├── 🐳 docker-compose.yml         # Container orchestration
├── 📖 README.md                  # Project documentation
├── ⚙️  setup.sh                  # Alternative setup script
├── backend/                      # FastAPI Backend
│   ├── 🔧 main.py               # FastAPI application entry point
│   ├── 🗄️  database.py          # Database configuration & connection
│   ├── 📊 models.py             # SQLAlchemy database models
│   ├── 📋 schemas.py            # Pydantic request/response schemas
│   ├── 📄 requirements.txt      # Python dependencies
│   ├── 🐳 Dockerfile            # Backend container configuration
│   └── services/                # Backend service modules
│       ├── 📄 pdf_processor.py  # PDF text extraction & OCR
│       ├── 🤖 llm_service.py    # AI/LLM integration (OpenAI, xAI)
│       └── 🔍 rag_service.py    # Vector database & RAG system
├── frontend/                     # React Frontend (if configured)
│   ├── src/
│   │   ├── components/          # Reusable React components
│   │   ├── pages/               # Page-level components
│   │   ├── contexts/            # React context providers
│   │   └── services/            # API communication services
│   ├── public/                  # Static assets
│   └── package.json             # Node.js dependencies
├── uploads/                      # Document storage (auto-created)
└── test files/                   # Testing utilities
    ├── test_backend.py
    ├── test_basic.py
    └── create_sample_pdf.py
```

## 🔧 Key Components

### Enhanced Bootstrap Script (`run.py`)
- **Smart dependency management** with multiple fallback strategies
- **Docker integration** for PostgreSQL database
- **System dependency installation** (build tools, PostgreSQL client)
- **Network resilience** handling PyPI connectivity issues
- **Comprehensive error reporting** with troubleshooting guidance
- **Cross-platform compatibility** (Linux, macOS, Windows with WSL)

### Backend Architecture (`backend/`)
- **FastAPI framework** for high-performance REST API
- **SQLAlchemy ORM** with PostgreSQL support
- **Modular services** for PDF processing, AI integration, and RAG
- **Containerized deployment** with Docker support
- **Comprehensive error handling** and logging

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

## 🎯 Configuration & Environment

### Environment Variables

The bootstrap script automatically sets up essential environment variables, but you can customize them:

```bash
# Database Configuration (auto-configured by bootstrap script)
DATABASE_URL=postgresql://dartos:dartos123@localhost:5432/dartos

# Optional: AI/LLM Integration
XAI_API_KEY=your_xai_api_key           # For xAI Grok API
OPENAI_API_KEY=your_openai_api_key     # Alternative LLM provider

# Optional: Customize server behavior
FASTAPI_HOST=0.0.0.0                   # Server host (default: 0.0.0.0)
FASTAPI_PORT=8000                      # Server port (default: 8000)
FASTAPI_RELOAD=false                   # Enable auto-reload in development
```

### Bootstrap Script Configuration

The enhanced `run.py` script automatically:
- Creates required directories (`uploads/`, `backend/chroma_db/`)
- Sets up PostgreSQL connection string
- Configures Docker container networking
- Handles system-level dependencies

### Docker Compose Configuration

For production or custom setups, modify `docker-compose.yml`:

```yaml
# Example customizations
services:
  backend:
    ports:
      - "8080:8000"  # Change external port
    environment:
      - DATABASE_URL=postgresql://custom_user:pass@db:5432/custom_db
    volumes:
      - ./custom_uploads:/app/uploads
```

### Development vs Production

**Development (Bootstrap Script):**
- Uses local PostgreSQL Docker container
- Hot-reload enabled for FastAPI
- Local file storage
- Debug logging enabled

**Production (Docker Compose Recommended):**
- All services containerized
- Production-optimized builds
- Volume persistence
- Environment variable management
- Load balancing support

## 🧪 Testing & Validation

### Validate Bootstrap Setup
```bash
# Test the bootstrap script setup
python run.py --docker-check           # Check Docker availability
python run.py --help                   # View all options

# Test Python imports (after installation)
python -c "import fastapi, uvicorn, sqlalchemy, psycopg2, pydantic; print('✓ All packages OK')"
```

### Backend API Testing
```bash
# Test API endpoints
curl http://localhost:8000/              # Health check
curl http://localhost:8000/docs          # API documentation

# Test database connection
python -c "
from backend.database import engine
try:
    with engine.connect() as conn:
        print('✓ Database connection OK')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
"
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
