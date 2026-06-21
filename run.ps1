# Ecosphere Startup Helper Script

Write-Host "=============================================" -ForegroundColor Green
Write-Host "       Ecosphere Carbon Ledger Platform      " -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Verify Python is available
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Error "Python was not found on your system PATH. Please ensure Python is installed."
    Exit 1
}

Write-Host "Select Deployment Version to Launch:" -ForegroundColor Cyan
Write-Host "1) Deploy Streamlit Data Dashboard (Port 8501)" -ForegroundColor Cyan
Write-Host "2) Launch Full-Stack Starlette API Server + Web UI (Port 8000)" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Choose [1 or 2, default is 1]"

if ($choice -eq "2") {
    Write-Host "Spinning up Starlette ASGI Server with Uvicorn..." -ForegroundColor Green
    Write-Host "Access the application at: http://127.0.0.1:8000" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C in this terminal window to stop the server." -ForegroundColor Yellow
    Write-Host ""
    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
} else {
    Write-Host "Spinning up Streamlit Data Application..." -ForegroundColor Green
    Write-Host "Access the application at: http://127.0.0.1:8501" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C in this terminal window to stop the server." -ForegroundColor Yellow
    Write-Host ""
    python -m streamlit run app_streamlit.py --server.port 8501 --server.address 127.0.0.1
}
