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

def install_requirements():
    """Install Python requirements"""
    print_step("Installing Python requirements...")
    
    requirements_path = Path("backend/requirements.txt")
    if not requirements_path.exists():
        print_error("requirements.txt not found in backend directory")
        return False
    
    # Try to install requirements
    result = run_command(f"{sys.executable} -m pip install -r {requirements_path}", check=False)
    if result.returncode != 0:
        print_warning("Failed to install requirements from pip (network issues?)")
        print_warning("Attempting to continue with existing packages...")
        
        # Check if essential packages are available
        essential_packages = ["fastapi", "uvicorn", "sqlalchemy", "psycopg2", "pydantic"]
        missing_packages = []
        
        for package in essential_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print_error(f"Missing essential packages: {', '.join(missing_packages)}")
            print_error("Please install packages manually with:")
            print_error(f"pip install {' '.join(missing_packages)}")
            return False
        else:
            print_warning("Essential packages found, continuing...")
            return True
    
    print_success("Python requirements installed successfully")
    return True

def start_postgres():
    """Start PostgreSQL in Docker"""
    print_step("Starting PostgreSQL in Docker...")
    
    # Check if postgres container is already running
    result = run_command("docker ps -q -f name=dartos-postgres", check=False)
    if result.stdout.strip():
        print_success("PostgreSQL container is already running")
        
        # Verify it's responding
        result = run_command("docker exec dartos-postgres pg_isready -U dartos", check=False)
        if result.returncode == 0:
            print_success("PostgreSQL is ready")
            return True
        else:
            print_warning("PostgreSQL container exists but not responding, restarting...")
    
    # Check if postgres container already exists but stopped
    result = run_command("docker ps -a -q -f name=dartos-postgres", check=False)
    if result.stdout.strip():
        print_warning("PostgreSQL container exists but stopped. Removing old container...")
        run_command("docker rm -f dartos-postgres", check=False)
    
    # Start PostgreSQL container
    postgres_cmd = """
    docker run -d \
        --name dartos-postgres \
        -e POSTGRES_DB=dartos \
        -e POSTGRES_USER=dartos \
        -e POSTGRES_PASSWORD=dartos123 \
        -p 5432:5432 \
        postgres:13
    """
    
    result = run_command(postgres_cmd.strip())
    if result.returncode != 0:
        print_error("Failed to start PostgreSQL container")
        return False
    
    # Wait for PostgreSQL to be ready
    print_step("Waiting for PostgreSQL to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        result = run_command(
            "docker exec dartos-postgres pg_isready -U dartos", 
            check=False
        )
        if result.returncode == 0:
            print_success("PostgreSQL is ready")
            return True
        time.sleep(1)
    
    print_error("PostgreSQL failed to start within 30 seconds")
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
    """Start the FastAPI server"""
    print_step("Starting FastAPI server on port 8000...")
    
    # Change to project root directory
    os.chdir(Path(__file__).parent)
    
    # Check if we can import the main module
    try:
        sys.path.insert(0, 'backend')
        import main
        print_success("Backend module imported successfully")
    except ImportError as e:
        print_error(f"Failed to import backend module: {e}")
        print_error("Make sure all required packages are installed")
        return False
    
    try:
        print(f"{Colors.GREEN}🌟 Server starting... Access at http://localhost:8000{Colors.ENDC}")
        print(f"{Colors.GREEN}📚 API Documentation: http://localhost:8000/docs{Colors.ENDC}")
        print(f"{Colors.YELLOW}Press Ctrl+C to stop the server{Colors.ENDC}")
        
        # Run the FastAPI server
        subprocess.run([sys.executable, "backend/main.py"])
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Shutting down server...{Colors.ENDC}")
        cleanup()
    except Exception as e:
        print_error(f"Failed to start server: {e}")
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
        print("\nUsage: python run.py [options]")
        print("\nOptions:")
        print("  --help, -h      Show this help message")
        print("  --skip-install  Skip Python package installation")
        print("\nThis script will:")
        print("1. Install Python requirements from backend/requirements.txt")
        print("2. Start PostgreSQL in Docker")
        print("3. Launch the FastAPI server on port 8000")
        return
    
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("🚀 Dartos Bootstrap Script")
    print("   Agentic Automated Info Services")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    
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
                print_warning("Package installation failed. Use --skip-install to bypass.")
                sys.exit(1)
        else:
            print_warning("Skipping package installation (--skip-install flag)")
        
        # Step 3: Start PostgreSQL
        if not start_postgres():
            sys.exit(1)
        
        # Step 4: Setup environment
        if not setup_environment():
            sys.exit(1)
        
        # Step 5: Start server
        if not start_server():
            sys.exit(1)
        
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()