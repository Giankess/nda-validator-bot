import subprocess
import sys
import os
from pathlib import Path

def run_command(command, shell=True):
    """Run a command and print its output in real-time."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=shell,
        universal_newlines=True
    )
    
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    return process.returncode

def setup_environment():
    """Set up the Python environment and install dependencies."""
    print("Setting up Python environment...")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        run_command(f"{sys.executable} -m venv venv")
    
    # Determine the pip path based on the OS
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # Upgrade pip
    print("Upgrading pip...")
    run_command(f"{python_path} -m pip install --upgrade pip")
    
    # Install requirements
    print("Installing requirements...")
    requirements_path = Path(__file__).parent.parent / "requirements.txt"
    run_command(f"{pip_path} install -r {requirements_path}")
    
    return python_path

def run_backend(python_path):
    """Run the FastAPI backend server."""
    print("\nStarting the backend server...")
    run_command(f"{python_path} -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")

def main():
    try:
        # Change to the backend directory
        os.chdir(Path(__file__).parent)
        
        # Set up environment
        python_path = setup_environment()
        
        # Run the backend
        run_backend(python_path)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 