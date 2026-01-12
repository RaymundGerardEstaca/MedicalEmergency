import sys
import os
import subprocess

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def main():
    print("[SETUP] Setting up and starting CCTV Unified Backend...")

    # 1. Check for venv
    venv_path = os.path.join(os.getcwd(), "venv")
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment in {venv_path}...")
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
    
    # 2. Determine pip/python paths
    if sys.platform == "win32":
        pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        pip_exe = os.path.join(venv_path, "bin", "pip")
        python_exe = os.path.join(venv_path, "bin", "python")

    # 3. Upgrade pip (optional but good practice)
    try:
        subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
    except subprocess.CalledProcessError:
        pass # Ignore upgrade errors

    # 4. Install dependencies
    print("[PKG] Installing requirements...")
    subprocess.check_call([pip_exe, "install", "-r", "requirements.txt"])

    # 5. Run Server
    print("[START] Starting Main Backend (FastAPI)...")
    print("   Listening on: http://0.0.0.0:8000")
    try:
        # Run main_backend.py using the venv python
        subprocess.check_call([python_exe, "main_backend.py"])
    except KeyboardInterrupt:
        print("\n[STOP] Server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Server failed with error code {e.returncode}")

if __name__ == "__main__":
    # Ensure we are in the backend directory
    if not os.path.exists("main_backend.py"):
        print("[ERROR] Please run this script from the 'backend' directory.")
        sys.exit(1)
    main()
