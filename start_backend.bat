@echo off
echo Starting Flask Backend Server...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
pause
