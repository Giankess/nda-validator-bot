import subprocess
import sys
import os
from pathlib import Path
import winreg  # For Windows registry access
import platform

def run_command(command, shell=False):
    """Run a command and print its output in real-time."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        shell=shell
    )
    
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    if process.returncode != 0:
        raise Exception(f"Command failed with return code {process.returncode}")
    return process.returncode

def enable_long_paths():
    """Enable Windows long path support."""
    if sys.platform == "win32":
        try:
            # Run the registry command to enable long paths
            run_command('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f')
            print("Enabled Windows long path support")
        except Exception as e:
            print(f"Warning: Could not enable long path support: {str(e)}")
            print("You may need to run this script as administrator")

def check_vc_build_tools():
    """Check if Visual C++ Build Tools are installed."""
    if sys.platform != "win32":
        return True
        
    try:
        # Check for Visual Studio Build Tools in registry
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\VisualStudio\14.0") as key:
            return True
    except WindowsError:
        return False

def get_python_version():
    """Get Python version in format like 'cp310' for Python 3.10."""
    version = sys.version_info
    return f"cp{version.major}{version.minor}0"

def get_platform_tag():
    """Get platform tag for wheel."""
    if sys.platform == "win32":
        return "win_amd64"
    elif sys.platform == "darwin":
        return "macosx_10_9_x86_64"
    else:
        return "manylinux_2_17_x86_64"

def setup_environment():
    """Set up the Python environment and install dependencies."""
    print("Setting up Python environment...")
    
    # Get the backend directory
    backend_dir = Path(__file__).parent.absolute()
    venv_path = backend_dir / ".venv"
    print(f"Using virtual environment at: {venv_path}")
    
    # Create virtual environment if it doesn't exist
    if not venv_path.exists():
        print("Creating virtual environment...")
        run_command([sys.executable, "-m", "venv", str(venv_path)])
    else:
        print("Virtual environment already exists. Cleaning up...")
        if sys.platform == "win32":
            run_command(["rmdir", "/s", "/q", str(venv_path)], shell=True)
        else:
            run_command(["rm", "-rf", str(venv_path)])
        run_command([sys.executable, "-m", "venv", str(venv_path)])
    
    # Determine the pip and python paths
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Upgrade pip
    print("Upgrading pip...")
    run_command([str(python_path), "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install dependencies from requirements.txt
    print("\nInstalling dependencies from requirements.txt...")
    requirements_path = backend_dir.parent / "requirements.txt"
    run_command([str(pip_path), "install", "-r", str(requirements_path)])
    
    return python_path

def run_backend(python_path):
    """Run the FastAPI backend server."""
    print("\nStarting the backend server...")
    try:
        run_command([str(python_path), "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    except Exception as e:
        print(f"Error starting the server: {str(e)}")
        print("\nTrying alternative method...")
        if sys.platform == "win32":
            uvicorn_path = Path(python_path).parent / "uvicorn"
        else:
            uvicorn_path = Path(python_path).parent / "uvicorn"
        run_command([str(uvicorn_path), "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])

def main():
    try:
        # Change to the backend directory
        backend_dir = Path(__file__).parent.absolute()
        os.chdir(backend_dir)
        print(f"Working directory: {os.getcwd()}")
        
        # Set up environment
        python_path = setup_environment()
        
        # Run the backend
        run_backend(python_path)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure you have Python 3.8 or higher installed")
        print("2. Try running these commands manually:")
        print(f'   {sys.executable} -m venv .venv')
        print('   .venv/bin/pip install --upgrade pip')
        print('   .venv/bin/pip install -r ../requirements.txt')
        print('   .venv/bin/python -m uvicorn main:app --reload')
        sys.exit(1)

if __name__ == "__main__":
    main() 