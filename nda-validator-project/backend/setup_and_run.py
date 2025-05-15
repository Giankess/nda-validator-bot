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
    if process.returncode != 0:
        raise Exception(f"Command failed with return code {process.returncode}")
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
    
    # First, install uvicorn separately to ensure it's available
    print("Installing uvicorn...")
    run_command(f"{pip_path} install uvicorn")
    
    # Then install the rest of the requirements
    print("Installing remaining requirements...")
    run_command(f"{pip_path} install -r {requirements_path}")
    
    # Verify uvicorn is installed
    print("Verifying uvicorn installation...")
    try:
        run_command(f"{python_path} -c 'import uvicorn'")
        print("Uvicorn installation verified successfully!")
    except Exception as e:
        print("Error: Uvicorn installation verification failed!")
        print("Trying to reinstall uvicorn...")
        run_command(f"{pip_path} install --force-reinstall uvicorn")
    
    return python_path

def run_backend(python_path):
    """Run the FastAPI backend server."""
    print("\nStarting the backend server...")
    try:
        run_command(f"{python_path} -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"Error starting the server: {str(e)}")
        print("\nTrying alternative method...")
        # Try running uvicorn directly
        if sys.platform == "win32":
            uvicorn_path = "venv\\Scripts\\uvicorn"
        else:
            uvicorn_path = "venv/bin/uvicorn"
        run_command(f"{uvicorn_path} main:app --reload --host 0.0.0.0 --port 8000")

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
        print("\nTroubleshooting steps:")
        print("1. Make sure you have Python 3.8 or higher installed")
        print("2. Try running these commands manually:")
        print("   python -m venv venv")
        print("   venv\\Scripts\\pip install --upgrade pip")
        print("   venv\\Scripts\\pip install uvicorn")
        print("   venv\\Scripts\\pip install -r ../requirements.txt")
        print("   venv\\Scripts\\python -m uvicorn main:app --reload")
        sys.exit(1)

if __name__ == "__main__":
    main() 