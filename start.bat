@echo off
REM Run the app locally on Windows and open it in the default browser.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv || goto :error
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :error
)
REM open the browser a few seconds after the server starts
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 4; Start-Process 'http://localhost:8501'"
".venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501
goto :eof
:error
echo Setup failed. Make sure Python 3.11+ is installed and on PATH.
pause
