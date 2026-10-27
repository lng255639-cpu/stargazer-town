@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "" "http://localhost:8765/"
python server.py
if errorlevel 1 (
  echo.
  echo 找不到 Python 或伺服器啟動失敗。請先安裝 Python 3：https://www.python.org/downloads/
  pause
)
