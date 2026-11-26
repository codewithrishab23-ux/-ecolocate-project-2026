@echo off
title EcoLocate Launcher
echo ========================================================
echo         EcoLocate - E-Waste Facility Locator
echo ========================================================
echo.

echo [1/3] Checking MySQL database on port 3307...
netstat -ano | findstr 3307 >nul
if %errorlevel% neq 0 (
    echo [INFO] Starting XAMPP MySQL on port 3307...
    start "" /B "C:\xampp\mysql\bin\mysqld.exe" --defaults-file="C:\xampp\mysql\bin\my.ini" --port=3307 --console
    timeout /t 3 /nobreak >nul
) else (
    echo [OK] MySQL is already running on port 3307.
)

echo.
echo [2/3] Verifying database connection...
python -c "import mysql.connector; conn = mysql.connector.connect(host='127.0.0.1', port=3307, user='root', password='', database='ewaste_db'); print('[OK] Connected to ewaste_db successfully!'); conn.close()"
if %errorlevel% neq 0 (
    echo [WARNING] Database connection check failed. Please check XAMPP.
)

echo.
echo [3/3] Starting Flask Web Server on http://127.0.0.1:5000 ...
echo Press Ctrl+C in this window to stop the server.
echo.
python app.py
pause
