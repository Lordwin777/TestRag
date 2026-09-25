@echo off
title AI Test Case Generator (RAG + Gemini)
cls

echo ======================================================================
echo           RAG-BASED AI TEST CASE GENERATOR - LAUNCHER
echo ======================================================================
echo.

:: 1. Verify Python availability
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your system PATH!
    echo Please install Python 3.10 or higher and make sure to check
    echo "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [+] Python environment detected:
python --version
echo.

:: 2. Ensure .env exists
if not exist ".env" (
    if exist ".env.example" (
        echo [*] Initializing .env configuration from .env.example...
        copy .env.example .env >nul
        echo [+] Created .env file. You can add your GEMINI_API_KEY there if desired.
        echo.
    )
)

:: 3. Build FAISS vector database if not already present
if not exist "vector_store\index.faiss" (
    echo [*] FAISS vector store index not found.
    echo [*] Automatically building vector store from knowledge_base documents...
    echo.
    python scripts\build_vector_store.py
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Failed to build the FAISS vector database.
        echo Please check the error message above.
        pause
        exit /b 1
    )
    echo.
) else (
    echo [+] FAISS vector database verified (vector_store\index.faiss ready).
)

:: 4. Launch notice & auto-open browser
echo.
echo ======================================================================
echo [+] Launching Flask Web Application...
echo [+] Server URL: http://127.0.0.1:5000
echo [+] Automatically opening dashboard in your default browser...
echo.
echo    * Press Ctrl+C in this terminal window to stop the server anytime.
echo ======================================================================
echo.

:: Launch browser in parallel after a 2-second delay to ensure Flask has bound the port
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"

:: 5. Start Flask web server
python app.py

if %errorlevel% neq 0 (
    echo.
    echo [NOTE] Server terminated.
    pause
)
