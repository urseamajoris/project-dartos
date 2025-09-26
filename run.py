#!/usr/bin/env python3
"""
Bootstrap script for Dartos - Agentic Automated Info Services

This script:
1. Installs Python requirements 
2. Starts PostgreSQL in Docker
3. Launches the FastAPI server on port 8000
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# Color codes for better output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(message):
    """Print a step with blue color"""
    print(f"{Colors.BLUE}{Colors.BOLD}🚀 {message}{Colors.ENDC}")

def print_success(message):
    """Print success message with green color"""
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_warning(message):
    """Print warning message with yellow color"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_error(message):
    """Print error message with red color"""
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        print_error(f"Error: {e.stderr}")
        return e

def check_docker():
    """Check if Docker is installed and running"""
    print_step("Checking Docker installation...")
    
    # Check if docker command exists
    result = run_command("docker --version", check=False)
    if result.returncode != 0:
        print_error("Docker is not installed. Please install Docker first.")
        return False
    
    # Check if Docker daemon is running
    result = run_command("docker info", check=False)
    if result.returncode != 0:
        print_error("Docker daemon is not running. Please start Docker.")
        return False
    
    print_success("Docker is installed and running")
    return True

def install_system_dependencies():
    """Install system-level dependencies required for Python packages"""
    print_step("Installing system dependencies...")
    
    system_packages = [
        "python3-dev", "python3-pip", "python3-venv", 
        "build-essential", "libpq-dev", "pkg-config"
    ]
    
    # Check if apt is available (Ubuntu/Debian)
    result = run_command("which apt", check=False)
    if result.returncode == 0:
        print_step("Installing system packages with apt...")
        apt_cmd = f"sudo apt update && sudo apt install -y {' '.join(system_packages)}"
        result = run_command(apt_cmd, check=False)
        if result.returncode != 0:
            print_warning("System package installation failed, continuing...")
    else:
        print_warning("apt not available, skipping system package installation")
    
    return True

def install_requirements():
    """Install Python requirements with multiple fallback strategies"""
    print_step("Installing Python requirements...")
    
    requirements_path = Path("backend/requirements.txt")
    if not requirements_path.exists():
        print_error("requirements.txt not found in backend directory")
        return False
    
    # First, install system dependencies
    install_system_dependencies()
    
    # Strategy 1: Try installing all requirements at once with longer timeout
    print_step("Attempting to install all requirements...")
    result = run_command(
        f"{sys.executable} -m pip install --timeout 60 --retries 2 -r {requirements_path}", 
        check=False
    )
    
    if result.returncode == 0:
        print_success("Python requirements installed successfully")
        return True
    
    print_warning("Bulk installation failed. Network connectivity issues detected.")
    
    # Strategy 2: Try with --no-deps for faster installation
    print_step("Trying installation without dependency resolution...")
    essential_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "psycopg2-binary", "pydantic", 
        "python-multipart", "python-dotenv"
    ]
    
    for package in essential_packages:
        print_step(f"Installing {package} (no deps)...")
        result = run_command(
            f"{sys.executable} -m pip install --no-deps --timeout 30 {package}", 
            check=False
        )
        if result.returncode == 0:
            print_success(f"✓ {package} installed")
        else:
            print_warning(f"⚠ {package} installation failed")
    
    # Strategy 3: Check if essential modules can be imported
    print_step("Checking if essential packages are available...")
    essential_imports = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("sqlalchemy", "sqlalchemy"),
        ("psycopg2", "psycopg2"),
        ("pydantic", "pydantic"),
    ]
    
    missing_packages = []
    available_packages = []
    
    for package_name, import_name in essential_imports:
        try:
            __import__(import_name)
            available_packages.append(package_name)
            print_success(f"✓ {package_name} is available")
        except ImportError:
            missing_packages.append(package_name)
            print_error(f"✗ {package_name} is not available")
    
    if missing_packages:
        print_error("\n" + "="*70)
        print_error("🚨 DEPENDENCY INSTALLATION FAILED")
        print_error("="*70)
        print_error("Network connectivity issues prevent package installation from PyPI.")
        print_error(f"\nMissing packages: {', '.join(missing_packages)}")
        print_error(f"Available packages: {', '.join(available_packages) if available_packages else 'None'}")
        
        print_error("\n💡 RECOMMENDED SOLUTIONS (in order of preference):")
        print_error("\n1. 🐳 USE DOCKER (Recommended)")
        print_error("   This bypasses Python package installation entirely:")
        print_error("   • docker-compose up")
        print_error("   • All dependencies are pre-installed in containers")
        
        print_error("\n2. 🌐 FIX NETWORK CONNECTIVITY")
        print_error("   • Check internet connection")
        print_error("   • Try again later (PyPI may be temporarily unavailable)")
        print_error("   • Configure pip proxy if behind corporate firewall")
        
        print_error("\n3. 🔧 MANUAL INSTALLATION")
        print_error("   • Create virtual environment: python -m venv venv")
        print_error("   • Activate: source venv/bin/activate (Linux) or venv\\Scripts\\activate (Windows)")
        print_error(f"   • Install: pip install {' '.join(missing_packages)}")
        print_error("   • Then run: python run.py --skip-install")
        
        print_error("\n4. 🏠 USE EXISTING ENVIRONMENT")
        print_error("   • If packages are installed elsewhere, try:")
        print_error("   • python run.py --skip-install")
        
        print_error("="*70)
        return False
    
    print_success("All essential packages are available!")
    print_success("Proceeding with server startup...")
    return True

def start_postgres():
    """Start PostgreSQL in Docker with enhanced reliability"""
    print_step("Starting PostgreSQL in Docker...")
    
    # Check if postgres container is already running
    result = run_command("docker ps -q -f name=dartos-postgres", check=False)
    if result.stdout.strip():
        print_success("PostgreSQL container is already running")
        
        # Verify it's responding
        for attempt in range(5):
            result = run_command("docker exec dartos-postgres pg_isready -U dartos", check=False)
            if result.returncode == 0:
                print_success("PostgreSQL is ready")
                return True
            time.sleep(2)
        
        print_warning("PostgreSQL container exists but not responding, restarting...")
        run_command("docker stop dartos-postgres", check=False)
        run_command("docker rm dartos-postgres", check=False)
    
    # Check if postgres container already exists but stopped
    result = run_command("docker ps -a -q -f name=dartos-postgres", check=False)
    if result.stdout.strip():
        print_warning("PostgreSQL container exists but stopped. Removing old container...")
        run_command("docker rm -f dartos-postgres", check=False)
    
    # Pull PostgreSQL image if not available
    print_step("Ensuring PostgreSQL image is available...")
    result = run_command("docker pull postgres:13", check=False)
    if result.returncode != 0:
        print_warning("Failed to pull postgres:13 image, trying with local image...")
    
    # Start PostgreSQL container with better configuration
    postgres_cmd = """docker run -d \
        --name dartos-postgres \
        --restart unless-stopped \
        -e POSTGRES_DB=dartos \
        -e POSTGRES_USER=dartos \
        -e POSTGRES_PASSWORD=dartos123 \
        -e POSTGRES_INITDB_ARGS="--auth-host=scram-sha-256 --auth-local=scram-sha-256" \
        -p 5432:5432 \
        -v dartos_postgres_data:/var/lib/postgresql/data \
        postgres:13"""
    
    print_step("Starting new PostgreSQL container...")
    result = run_command(postgres_cmd, check=False)
    if result.returncode != 0:
        print_error("Failed to start PostgreSQL container")
        print_error(f"Error output: {result.stderr}")
        return False
    
    # Wait for PostgreSQL to be ready with better feedback
    print_step("Waiting for PostgreSQL to initialize and be ready...")
    max_attempts = 60  # Increased timeout for initialization
    
    for attempt in range(max_attempts):
        # First check if container is still running
        result = run_command("docker ps -q -f name=dartos-postgres", check=False)
        if not result.stdout.strip():
            print_error("PostgreSQL container stopped unexpectedly")
            # Show container logs for debugging
            logs_result = run_command("docker logs dartos-postgres 2>&1 | tail -20", check=False)
            if logs_result.stdout:
                print_error("Container logs:")
                print_error(logs_result.stdout)
            return False
        
        # Check if PostgreSQL is ready
        result = run_command("docker exec dartos-postgres pg_isready -U dartos", check=False)
        if result.returncode == 0:
            print_success("PostgreSQL is ready!")
            
            # Test database connection
            test_cmd = 'docker exec dartos-postgres psql -U dartos -d dartos -c "SELECT version();"'
            result = run_command(test_cmd, check=False)
            if result.returncode == 0:
                print_success("Database connection test successful")
                return True
            else:
                print_warning("Database connection test failed, but proceeding...")
                return True
        
        # Show progress
        if attempt % 10 == 0 and attempt > 0:
            print_step(f"Still waiting... ({attempt}/{max_attempts} attempts)")
        
        time.sleep(1)
    
    print_error("PostgreSQL failed to start within 60 seconds")
    
    # Show container logs for debugging
    print_error("Container logs:")
    logs_result = run_command("docker logs dartos-postgres 2>&1 | tail -20", check=False)
    if logs_result.stdout:
        print_error(logs_result.stdout)
    
    return False

def setup_environment():
    """Setup environment variables"""
    print_step("Setting up environment...")
    
    # Set DATABASE_URL for PostgreSQL
    os.environ["DATABASE_URL"] = "postgresql://dartos:dartos123@localhost:5432/dartos"
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    # Create chroma_db directory if it doesn't exist  
    chroma_dir = Path("backend/chroma_db")
    chroma_dir.mkdir(exist_ok=True)
    
    print_success("Environment setup complete")
    return True

def start_server():
    """Start the FastAPI server with enhanced error handling"""
    print_step("Starting FastAPI server on port 8000...")
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    print_step(f"Working directory: {project_root}")
    
    # Add backend to Python path
    backend_path = project_root / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    
    # Check if we can import required modules
    try:
        print_step("Testing Python module imports...")
        
        # Test core dependencies
        import fastapi
        print_success(f"✓ FastAPI {fastapi.__version__}")
        
        import uvicorn
        print_success(f"✓ Uvicorn {uvicorn.__version__}")
        
        import sqlalchemy
        print_success(f"✓ SQLAlchemy {sqlalchemy.__version__}")
        
        # Test backend modules
        import database
        print_success("✓ Database module")
        
        import models
        print_success("✓ Models module")
        
        # Try importing main module
        import main
        print_success("✓ Main backend module imported successfully")
        
    except ImportError as e:
        print_error(f"Failed to import required modules: {e}")
        print_error("This suggests missing or incompatible packages.")
        print_error("\nTroubleshooting steps:")
        print_error("1. Try running: pip install -r backend/requirements.txt")
        print_error("2. Check if you're in a virtual environment")
        print_error("3. Use: python run.py --skip-install if packages are installed elsewhere")
        return False
    except Exception as e:
        print_error(f"Unexpected error importing modules: {e}")
        return False
    
    # Check if port 8000 is available
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('localhost', 8000))
        if result == 0:
            print_warning("Port 8000 is already in use")
            print_warning("If this is another instance of the server, stop it first")
    
    try:
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}🌟 Starting Dartos Server{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.GREEN}🌐 Server URL: http://localhost:8000{Colors.ENDC}")
        print(f"{Colors.GREEN}📚 API Documentation: http://localhost:8000/docs{Colors.ENDC}")
        print(f"{Colors.GREEN}🗄️  Database: PostgreSQL (dartos-postgres){Colors.ENDC}")
        print(f"{Colors.YELLOW}⚡ Press Ctrl+C to stop the server{Colors.ENDC}\n")
        
        # Start the server using uvicorn directly for better control
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload in bootstrap mode
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}🛑 Shutting down server...{Colors.ENDC}")
        cleanup()
    except Exception as e:
        print_error(f"Failed to start server: {e}")
        print_error("Check the error above and try the troubleshooting steps")
        return False
    
    return True

def cleanup():
    """Cleanup resources on exit"""
    print_step("Cleaning up...")
    
    # Stop PostgreSQL container
    result = run_command("docker stop dartos-postgres", check=False)
    if result.returncode == 0:
        print_success("PostgreSQL container stopped")
    
    # Remove PostgreSQL container
    result = run_command("docker rm dartos-postgres", check=False)
    if result.returncode == 0:
        print_success("PostgreSQL container removed")

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print(f"\n{Colors.YELLOW}Received interrupt signal. Cleaning up...{Colors.ENDC}")
    cleanup()
    sys.exit(0)

def main():
    """Main bootstrap function"""
    # Check for help flag
    if "--help" in sys.argv or "-h" in sys.argv:
        print(f"{Colors.BOLD}{Colors.BLUE}Dartos Bootstrap Script{Colors.ENDC}")
        print(f"{Colors.BOLD}Agentic Automated Info Services{Colors.ENDC}")
        print("\nUsage: python run.py [options]")
        print("\nOptions:")
        print("  --help, -h      Show this help message")
        print("  --skip-install  Skip Python package installation")
        print("  --docker-check  Check if Docker Compose setup is available")
        print("\nThis script will:")
        print("1. Install system dependencies (build tools, PostgreSQL client)")
        print("2. Install Python requirements from backend/requirements.txt")
        print("3. Start PostgreSQL database in Docker")
        print("4. Set up environment variables and directories")
        print("5. Launch the FastAPI server on port 8000")
        print("\nAlternative Setup Methods:")
        print("• Docker Compose (Recommended): docker-compose up")
        print("• Docker with Bootstrap: Use this script after 'docker-compose build'")
        print("\nTroubleshooting:")
        print("• If package installation fails due to network issues, the script")
        print("  will provide specific guidance for your situation")
        print("• Use --skip-install if dependencies are already installed")
        print("• Check logs above if any step fails for specific error details")
        return
    
    # Check for docker-check flag
    if "--docker-check" in sys.argv:
        print(f"{Colors.BOLD}{Colors.BLUE}Checking Docker Compose Setup{Colors.ENDC}")
        
        compose_file = Path("docker-compose.yml")
        if compose_file.exists():
            print_success("✓ docker-compose.yml found")
            print_step("You can use Docker Compose instead:")
            print(f"{Colors.GREEN}  docker-compose up{Colors.ENDC}")
            print(f"{Colors.GREEN}  # This will start all services in containers{Colors.ENDC}")
        else:
            print_warning("✗ docker-compose.yml not found")
        
        return
    
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 70)
    print("🚀 Dartos Bootstrap Script")
    print("   Agentic Automated Info Services")
    print("   Enhanced Dependency Management & Docker Integration")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    
    # Show Docker Compose alternative
    compose_file = Path("docker-compose.yml")
    if compose_file.exists():
        print(f"{Colors.YELLOW}💡 Alternative: For a fully containerized setup, run:{Colors.ENDC}")
        print(f"{Colors.YELLOW}   docker-compose up{Colors.ENDC}")
        print(f"{Colors.YELLOW}   (This bypasses Python package installation){Colors.ENDC}")
        print("")
    
    # Parse command line arguments
    skip_install = "--skip-install" in sys.argv
    
    # Register signal handlers for cleanup
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Step 1: Check Docker
        if not check_docker():
            sys.exit(1)
        
        # Step 2: Install requirements (unless skipped)
        if not skip_install:
            if not install_requirements():
                print_error("\n" + "="*70)
                print_error("🚨 BOOTSTRAP FAILED - DEPENDENCY INSTALLATION")
                print_error("="*70)
                print_error("The bootstrap script could not install required Python packages.")
                print_error("This is likely due to network connectivity issues with PyPI.")
                print_error("\n🐳 RECOMMENDED: Use Docker Compose instead")
                print_error("   docker-compose up")
                print_error("   # All dependencies are pre-installed in containers")
                print_error("\n🔧 Alternative: Manual installation")
                print_error("   pip install -r backend/requirements.txt")
                print_error("   python run.py --skip-install")
                sys.exit(1)
        else:
            print_warning("Skipping package installation (--skip-install flag)")
        
        # Step 3: Start PostgreSQL
        if not start_postgres():
            print_error("PostgreSQL setup failed. Check Docker logs above.")
            sys.exit(1)
        
        # Step 4: Setup environment
        if not setup_environment():
            sys.exit(1)
        
        # Step 5: Start server
        if not start_server():
            sys.exit(1)
        
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        print_error("Traceback:")
        print_error(traceback.format_exc())
        cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()