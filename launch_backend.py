#!/usr/bin/env python3
"""Launch the FastAPI backend with correct working directory."""

import os
import sys
import subprocess

# Change to backend directory
backend_dir = r"C:\Users\gadda\OneDrive\Desktop\job\candidate-screening-ai\backend"
os.chdir(backend_dir)

print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.executable}")
print()

# Start uvicorn
try:
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--port", "8000",
        "--host", "127.0.0.1"
    ])
except KeyboardInterrupt:
    print("\n\nServer stopped.")
    sys.exit(0)
