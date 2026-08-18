@echo off
cd /d "C:\Users\gadda\OneDrive\Desktop\job\candidate-screening-ai\backend"
python -m uvicorn app.main:app --reload --port 8000
pause
